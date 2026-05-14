###
# Copyright © 2017 - 2026, Barry Suridge
# All rights reserved.
#
###

from typing import Awaitable, Callable, Optional

import aiohttp
from supybot import callbacks, log


async def create_session(
    headers: dict[str, str], timeout_seconds: int
) -> aiohttp.ClientSession:
    """Create the shared aiohttp session for the plugin."""
    timeout = aiohttp.ClientTimeout(total=timeout_seconds)
    return aiohttp.ClientSession(headers=headers, timeout=timeout)


async def fetch_json(
    session: Optional[aiohttp.ClientSession],
    url: str,
    params: dict,
    error_handler: Callable[..., object],
) -> dict:
    """Fetch JSON data from the given URL with specified parameters."""
    if session is None:
        error_handler(
            RuntimeError("aiohttp session is unavailable"),
            context=f"Fetching data from {url}",
            user_message="Weather HTTP session is unavailable. Please try again later.",
        )

    try:
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientResponseError as error:
        error_handler(error, context=f"HTTP error for {url}")
    except Exception as error:
        error_handler(error, context=f"Fetching data from {url}")


async def google_maps(
    fetcher: Callable[[str, dict], Awaitable[dict]],
    api_key: str,
    address: str,
    error_handler: Callable[..., object],
) -> tuple[str, float, float, str, str]:
    """Get location data from the Google Maps API."""
    if not api_key:
        raise callbacks.Error(
            "Google Maps API key is missing. Configure it with plugins.Weather.googlemapsAPI [your_key]."
        )

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}
    log.debug(f"Using Google Maps API with {url}")

    data = await fetcher(url, params)
    if data.get("status") != "OK":
        error_handler(
            RuntimeError(data.get("status", "Unknown error")),
            context=f"Google Maps API for address {address}",
        )

    result = data["results"][0]
    lat = result["geometry"]["location"]["lat"]
    lng = result["geometry"]["location"]["lng"]
    postcode = next(
        (
            component["short_name"]
            for component in result.get("address_components", [])
            if "postal_code" in component.get("types", [])
        ),
        "N/A",
    )
    place_id = result.get("place_id", "N/A")
    formatted_address = result.get("formatted_address", "Unknown location")

    return formatted_address, lat, lng, postcode, place_id


async def openweather(
    fetcher: Callable[[str, dict], Awaitable[dict]],
    api_key: str,
    lat: float,
    lon: float,
) -> dict:
    """Fetch weather data from the OpenWeather API."""
    if not api_key:
        raise callbacks.Error(
            "Please configure the OpenWeather API key via plugins.Weather.openweatherAPI [your_key_here]"
        )

    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "exclude": "hourly,minutely,alerts",
        "appid": api_key,
        "units": "metric",
    }
    log.debug(f"Weather: using URL {url} (openweather)")
    return await fetcher(url, params)
