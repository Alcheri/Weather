###
# Copyright © 2017 - 2026, Barry Suridge
# All rights reserved.
#
###

from datetime import datetime, timezone
import math

from supybot import ircutils

APOSTROPHE = "\N{APOSTROPHE}"
DEGREE_SIGN = "\N{DEGREE SIGN}"
PERCENT_SIGN = "\N{PERCENT SIGN}"
QUOTATION_MARK = "\N{QUOTATION MARK}"


def colour_uvi(uvi: float) -> str:
    """Assign a descriptive text and colour to the UV Index value."""
    ranges = [
        (0, 3, "light green", "Low"),
        (3, 6, "yellow", "Moderate"),
        (6, 8, "orange", "High"),
        (8, 11, "red", "Very High"),
        (11, float("inf"), "purple", "Extreme"),
    ]

    if uvi < 0:
        return ircutils.mircColor("Unknown UVI", "light grey")

    for lower, upper, colour, description in ranges:
        if lower <= uvi < upper:
            return ircutils.mircColor(f"UVI {uvi} ({description})", colour)

    return ircutils.mircColor("UVI Unknown", "grey")


def colour_temperature(celsius: float) -> str:
    """Colourise and format temperatures."""
    ranges = [
        (float("-inf"), 0, "blue"),
        (0, 1, "teal"),
        (1, 10, "light blue"),
        (10, 20, "light green"),
        (20, 30, "yellow"),
        (30, 40, "orange"),
        (40, float("inf"), "red"),
    ]

    celsius = float(celsius)
    for lower, upper, colour in ranges:
        if lower <= celsius < upper:
            return ircutils.mircColor(f"{celsius}{DEGREE_SIGN}C", colour)

    return ircutils.mircColor(f"{celsius}{DEGREE_SIGN}C", "grey")


def dd2dms(longitude: float, latitude: float) -> tuple[str, str]:
    """Convert decimal degrees to degrees, minutes, and seconds."""

    def convert(coord: float) -> tuple[int, int, float]:
        split_deg = math.modf(coord)
        degrees = int(split_deg[1])
        minutes = abs(int(math.modf(split_deg[0] * 60)[1]))
        seconds = abs(round(math.modf(split_deg[0] * 60)[0] * 60, 2))
        return degrees, minutes, seconds

    degrees_x, minutes_x, seconds_x = convert(longitude)
    degrees_y, minutes_y, seconds_y = convert(latitude)

    x = (
        f"{abs(degrees_x)}{DEGREE_SIGN}{minutes_x}{APOSTROPHE} "
        f'{seconds_x}{QUOTATION_MARK} {"W" if degrees_x < 0 else "E"}'
    )
    y = (
        f"{abs(degrees_y)}{DEGREE_SIGN}{minutes_y}{APOSTROPHE} "
        f'{seconds_y}{QUOTATION_MARK} {"S" if degrees_y < 0 else "N"}'
    )
    return x, y


def format_location(lat: float, lon: float, location: str) -> str:
    """Format location and coordinates for display."""
    lat_dms, lon_dms = dd2dms(lon, lat)
    return f"{location} (Lat: {lat_dms}, Lon: {lon_dms})"


def get_wind_direction(degrees: float) -> str:
    """Calculate and return the wind direction as text."""
    directions = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]
    degrees = degrees % 360
    return directions[int((degrees / 22.5) + 0.5) % 16]


def format_current_conditions(current: dict) -> str:
    """Format current weather conditions for display."""
    temp = colour_temperature(round(current["temp"]))
    feels_like = colour_temperature(round(current["feels_like"]))
    desc = current["weather"][0]["description"].capitalize()
    humidity = f"Humidity: {current['humidity']}{PERCENT_SIGN}"
    cloud = f"Clouds: {current['clouds']}"
    wind_speed = f"Wind: {round(current['wind_speed'] * 3.6)} Km/h"
    wind_direction = get_wind_direction(current["wind_deg"])
    uvi_index = colour_uvi(round(current["uvi"]))

    return (
        f"{desc}, Temp: {temp}, "
        f"Feels like: {feels_like}, "
        f"{humidity}, "
        f"{cloud}{PERCENT_SIGN}, "
        f"{wind_speed}, {wind_direction}, "
        f"UV Index: {uvi_index}"
    )


def format_weather_results(location: str, weather_data: dict) -> str:
    """Format weather data for display."""
    return " | ".join(
        [
            format_location(weather_data["lat"], weather_data["lon"], location),
            format_current_conditions(weather_data["current"]),
        ]
    )


def format_forecast_results(location: str, weather_data: dict) -> str:
    """Format multi-day forecast data for display."""
    formatted_data = [f"Forecast for {location}:"]

    for day in weather_data["daily"][:5]:
        date = datetime.fromtimestamp(day["dt"], tz=timezone.utc).strftime("%A")
        desc = day["weather"][0]["description"].capitalize()
        min_temp = colour_temperature(round(day["temp"]["min"]))
        max_temp = colour_temperature(round(day["temp"]["max"]))
        formatted_data.append(f"{date}: {desc}, Min: {min_temp}, Max: {max_temp}")

    return " | ".join(formatted_data)
