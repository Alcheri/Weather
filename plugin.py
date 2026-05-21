###
# Copyright © 2017 - 2026, Barry Suridge
# All rights reserved.
#
###
#
# A fully asynchronous Weather plugin for Limnoria using the OpenWeather and
# Google Maps APIs.
#
##

import threading
import time
from concurrent.futures import TimeoutError as FutureTimeoutError
from typing import NoReturn, Optional

try:
    import aiohttp  # asynchronous HTTP client and server framework
    import asyncio  # asynchronous I/O
except ImportError as ie:
    raise ImportError(f"Cannot import module: {ie}")

import supybot.conf as conf
import supybot.world as world
from supybot import callbacks, ircutils, log
from supybot.commands import additional, getopts, wrap

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("Weather")
except ImportError:

    def _(text):
        return text


from .local import client, formatting, storage

HEADERS = {
    "User-Agent": "Limnoria-Weather/1.1 (+https://github.com/Alcheri/Weather)"
}
REQUEST_TIMEOUT_SECONDS = 10
FILENAME = conf.supybot.directories.data.dirize("Weather.json")
MAX_LOCATION_LENGTH = 160
MAX_REPLY_LENGTH = 450
IRC_FORMATTING_CONTROLS = {"\x02", "\x03", "\x0f", "\x16", "\x1d", "\x1f"}


def _clean_location(location: str) -> str:
    cleaned = " ".join(location.split()).strip().lower()
    cleaned = "".join(char for char in cleaned if not _is_unsafe_control(char))
    if not cleaned:
        raise callbacks.Error("Location cannot be empty.")
    if len(cleaned) > MAX_LOCATION_LENGTH:
        raise callbacks.Error(
            f"Location is too long; use {MAX_LOCATION_LENGTH} characters or fewer."
        )
    return cleaned


def _is_unsafe_control(char: str) -> bool:
    return ord(char) < 32 and char not in ("\t",)


def _safe_log_context(context: Optional[str]) -> str:
    if not context:
        return "No additional context provided."
    cleaned = "".join(
        char if not _is_unsafe_control(char) else " " for char in context
    )
    return " ".join(cleaned.split())[:160]


def _safe_reply(text: str, limit: int = MAX_REPLY_LENGTH) -> str:
    cleaned = []
    for char in text.replace("\r", " ").replace("\n", " "):
        if char in IRC_FORMATTING_CONTROLS or not _is_unsafe_control(char):
            cleaned.append(char)
    result = " ".join("".join(cleaned).split())
    if len(result) <= limit:
        return result
    return result[: limit - 1].rstrip() + "\u2026"


class CooldownTracker:
    """Track per-user command cooldowns."""

    def __init__(self):
        self._seen = {}
        self._lock = threading.Lock()

    def remaining(self, key, cooldown_seconds):
        cooldown_seconds = max(0, int(cooldown_seconds or 0))
        if cooldown_seconds <= 0:
            return 0

        now = time.monotonic()
        with self._lock:
            self._seen = {
                item: last_seen
                for item, last_seen in self._seen.items()
                if now - last_seen < cooldown_seconds
            }
            last_seen = self._seen.get(key)
            if last_seen is None or now - last_seen >= cooldown_seconds:
                self._seen[key] = now
                return 0
            return max(1, int(cooldown_seconds - (now - last_seen)))


def handle_error(
    error: Exception,
    context: Optional[str] = None,
    user_message: str = "An error occurred.",
) -> NoReturn:
    """Log and handle errors gracefully."""
    log.error(
        "Weather error: %s | Context: %s",
        error.__class__.__name__,
        _safe_log_context(context),
    )
    raise callbacks.Error(user_message)


class Weather(callbacks.Plugin):
    """
    Provides current weather conditions and multi-day forecasts using the
    OpenWeather and Google Maps APIs.  Use 'weather <location>' for current
    conditions, 'weather --forecast <location>' for a 5-day forecast, and
    'set <location>' to save a default location for your hostmask.
    Get the current weather for the specified location,
    or a default location.
    """

    threaded = True

    def __init__(self, irc):
        super().__init__(irc)
        self._store = storage.WeatherLocationStore(FILENAME)
        self.db = self._store.load()
        self.cooldowns = CooldownTracker()
        world.flushers.append(self.flush_db)
        self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(
            target=self._run_loop, name="WeatherAsyncLoop", daemon=True
        )
        self._session: Optional[aiohttp.ClientSession] = None
        self._loop_thread.start()
        try:
            self._session = self._run_coro_threadsafe(self._create_session())
        except Exception as error:
            log.error(f"Weather: failed to create aiohttp session: {error}")

    async def _create_session(self):
        return await client.create_session(HEADERS, REQUEST_TIMEOUT_SECONDS)

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def _run_coro_threadsafe(
        self, coro, timeout: int = REQUEST_TIMEOUT_SECONDS
    ):
        if self._loop.is_closed():
            raise RuntimeError("Weather event loop is closed.")
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        try:
            return future.result(timeout=timeout)
        except FutureTimeoutError as error:
            future.cancel()
            raise RuntimeError("Timed out waiting for async task.") from error

    def load_db(self):
        self.db = self._store.load()
        return self.db

    def flush_db(self):
        self._store.flush()

    def die(self):
        if self._session is not None:
            try:
                self._run_coro_threadsafe(self._session.close())
            except Exception as error:
                log.warning(f"Weather: error closing aiohttp session: {error}")
        try:
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._loop_thread.join(timeout=REQUEST_TIMEOUT_SECONDS)
            if self._loop_thread.is_alive():
                log.warning("Weather: event loop thread did not stop cleanly.")
            self._loop.close()
        except Exception as error:
            log.warning(f"Weather: error closing event loop: {error}")
        self.flush_db()
        world.flushers.remove(self.flush_db)
        super().die()

    @staticmethod
    def colour_uvi(uvi: float) -> str:
        return formatting.colour_uvi(uvi)

    @staticmethod
    def colour_temperature(celsius: float) -> str:
        return formatting.colour_temperature(celsius)

    def dd2dms(self, longitude, latitude):
        return formatting.dd2dms(longitude, latitude)

    def format_location(self, lat: float, lon: float, location: str) -> str:
        return formatting.format_location(lat, lon, location)

    def format_current_conditions(self, current: dict) -> str:
        return formatting.format_current_conditions(current)

    @staticmethod
    def _get_wind_direction(degrees: float) -> str:
        return formatting.get_wind_direction(degrees)

    async def fetch_data(self, url: str, params: dict) -> dict:
        return await client.fetch_json(
            self._session, url, params, handle_error
        )

    async def google_maps(self, address: str) -> tuple:
        return await client.google_maps(
            self.fetch_data,
            self.registryValue("googlemapsAPI"),
            address,
            handle_error,
        )

    async def openweather(self, lat, lon):
        return await client.openweather(
            self.fetch_data, self.registryValue("openweatherAPI"), lat, lon
        )

    async def format_weather_results(
        self, location: str, weather_data: dict
    ) -> str:
        return formatting.format_weather_results(location, weather_data)

    async def format_forecast_results(self, location, weather_data):
        return formatting.format_forecast_results(location, weather_data)

    def _is_enabled(self, irc, msg) -> bool:
        return bool(self.registryValue("enabled", msg.channel, irc.network))

    def _cooldown_remaining(self, irc, msg, command: str) -> int:
        cooldown = self.registryValue(
            "cooldownSeconds", msg.channel, irc.network
        )
        key = (irc.network, msg.channel, msg.prefix, command)
        return self.cooldowns.remaining(key, cooldown)

    def _enforce_cooldown(self, irc, msg, command: str) -> bool:
        cooldown = self._cooldown_remaining(irc, msg, command)
        if not cooldown:
            return True
        irc.error(
            f"Please wait {cooldown}s before using Weather again.",
            prefixNick=False,
        )
        return False

    @wrap([getopts({"user": "nick", "forecast": ""}), additional("text")])
    def weather(self, irc, msg, args, optlist, location=None):
        """[--user <nick>] [--forecast] [-- <location>]

        Get the current weather for the specified location, or a default location.
        """
        if not self._is_enabled(irc, msg):
            return
        if not self._enforce_cooldown(irc, msg, "weather"):
            return

        optlist = dict(optlist)
        if not location:
            ident_host = None
            try:
                if "user" in optlist:
                    host = irc.state.nickToHostmask(optlist["user"])
                else:
                    host = msg.prefix
                if not host or "!" not in host:
                    irc.error(
                        "Unable to determine a hostmask for that nickname.",
                        Raise=True,
                    )
                    return
                ident_host = host.split("!", 1)[1]
                location = self._store.get(ident_host)
            except KeyError:
                if ident_host is None:
                    irc.error(
                        f"Nickname {ircutils.bold(optlist['user'])} not found in channel.",
                        Raise=True,
                    )
                else:
                    irc.error(
                        "No location for %s is set. Use the \u2018set\u2019 command "
                        "to set a location for your current hostmask, or call \u2018weather\u2019 "
                        "with <location> as an argument."
                        % ircutils.bold("*!" + ident_host),
                        Raise=True,
                    )
        if location is None:
            irc.error("No location was provided.", Raise=True)
            return
        location = _clean_location(location)

        async def process_weather():
            try:
                formatted_address, lat, lon, _, _ = await self.google_maps(
                    location
                )
                weather_data = await self.openweather(lat, lon)
                if "forecast" in optlist:
                    return await self.format_forecast_results(
                        formatted_address, weather_data
                    )
                return await self.format_weather_results(
                    formatted_address, weather_data
                )
            except Exception as error:
                handle_error(
                    error,
                    context=f"Processing weather command for location: {location}",
                )

        try:
            result = self._run_coro_threadsafe(process_weather())
            if result:
                irc.reply(_safe_reply(result), prefixNick=False)
        except Exception as error:
            handle_error(error, context="Executing weather command")

    @wrap(["text"])
    def set(self, irc, msg, args, location):
        """<location>

        Set a default location for your current hostmask.
        """
        ident_host = msg.prefix.split("!")[1]
        self._store.set(ident_host, _clean_location(location))
        irc.replySuccess()

    @wrap([])
    def unset(self, irc, msg, args):
        """
        Unset the default location for your current hostmask.
        """
        ident_host = msg.prefix.split("!")[1]
        if self._store.unset(ident_host):
            irc.replySuccess()
        else:
            irc.error("No default location set for your hostmask.")

    @wrap(["text"])
    def google(self, irc, msg, args, location):
        """Look up <location>

        [city <(Alpha-2) country code>] [<postcode, (Alpha-2) country code>] [latitude, longitude]
        <address>
        """
        if not self._is_enabled(irc, msg):
            return
        if not self._enforce_cooldown(irc, msg, "google"):
            return
        location = _clean_location(location)

        async def process_google():
            try:
                display_name, lat, lng, postcode, place_id = (
                    await self.google_maps(location)
                )
                formatted_txt = (
                    f"\x02{display_name}\x02 \x02{postcode}\x02 [ID: {place_id}] "
                    f"\x02{lat}\x02 \x02{lng}\x02"
                )
                irc.reply(
                    _safe_reply(f"From Google Maps: {formatted_txt}"),
                    prefixNick=False,
                )
            except Exception as error:
                handle_error(
                    error,
                    context=f"Processing Google command for location: {location}",
                )

        self._run_coro_threadsafe(process_google())


Class = Weather

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
