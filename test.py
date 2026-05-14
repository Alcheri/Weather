###
# Copyright (c) 2017 - 2026, Barry Suridge
# All rights reserved.
###

import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
import unittest
from unittest.mock import AsyncMock, patch

import supybot.conf as conf
import supybot.test as supybot_test
import supybot.world as world

if not hasattr(world, "myVerbose"):
    world.myVerbose = 0

if not hasattr(conf.supybot.networks, "test"):
    conf.registerNetwork("test")


class WeatherTestCase(supybot_test.PluginTestCase):
    # Keep this for Limnoria's native plugin test harness; pytest should ignore it.
    __test__ = False
    plugins = ("Weather",)


class WeatherCommandTestCase(supybot_test.PluginTestCase):
    plugins = ("Weather",)

    def runTest(self):
        pass

    def setUp(self):
        self._original_plugin_dirs = conf.supybot.directories.plugins()
        conf.supybot.directories.plugins.setValue(["/home/barry/supyplugins"])
        super().setUp()
        self.cb = self.irc.getCallback("Weather")
        self._original_flush_db = self.cb.flush_db
        if self._original_flush_db in world.flushers:
            world.flushers.remove(self._original_flush_db)
        self.cb.flush_db = lambda: None
        world.flushers.append(self.cb.flush_db)
        self.cb.db.clear()

    def tearDown(self):
        self.cb.db.clear()
        conf.supybot.directories.plugins.setValue(self._original_plugin_dirs)
        super().tearDown()

    @staticmethod
    def _enabled_registry_value(name, *args):
        if name == "enabled":
            return True
        raise AssertionError(f"Unexpected registry lookup: {name} {args}")

    def test_set_stores_default_location_for_hostmask(self):
        self.assertNotError("set Ballarat VIC AU", frm="alice!user@example.test")

        self.assertEqual(self.cb.db["user@example.test"], "ballarat vic au")

    def test_unset_removes_default_location_for_hostmask(self):
        self.cb.db["user@example.test"] = "ballarat vic au"

        self.assertNotError("unset", frm="alice!user@example.test")

        self.assertNotIn("user@example.test", self.cb.db)

    def test_google_replies_with_google_maps_result(self):
        with patch.object(
            self.cb,
            "google_maps",
            new=AsyncMock(
                return_value=(
                    "Ballarat VIC 3350, Australia",
                    -37.5621587,
                    143.8502556,
                    "3350",
                    "place-123",
                )
            ),
        ) as google_maps:
            self.assertResponse(
                "google Ballarat VIC AU",
                "From Google Maps: \x02Ballarat VIC 3350, Australia\x02 "
                "\x023350\x02 [ID: place-123] \x02-37.5621587\x02 "
                "\x02143.8502556\x02",
            )

        google_maps.assert_awaited_once_with("ballarat vic au")

    def test_weather_replies_for_explicit_location(self):
        with (
            patch.object(
                self.cb, "registryValue", side_effect=self._enabled_registry_value
            ),
            patch.object(
                self.cb,
                "google_maps",
                new=AsyncMock(
                    return_value=(
                        "Ballarat VIC 3350, Australia",
                        -37.5621587,
                        143.8502556,
                        "3350",
                        "place-123",
                    )
                ),
            ) as google_maps,
            patch.object(
                self.cb, "openweather", new=AsyncMock(return_value={"current": {}})
            ) as openweather,
            patch.object(
                self.cb,
                "format_weather_results",
                new=AsyncMock(return_value="Current weather output"),
            ) as format_weather,
        ):
            self.assertResponse("weather Ballarat VIC AU", "Current weather output")

        google_maps.assert_awaited_once_with("ballarat vic au")
        openweather.assert_awaited_once_with(-37.5621587, 143.8502556)
        format_weather.assert_awaited_once_with(
            "Ballarat VIC 3350, Australia", {"current": {}}
        )

    def test_weather_forecast_replies_for_explicit_location(self):
        with (
            patch.object(
                self.cb, "registryValue", side_effect=self._enabled_registry_value
            ),
            patch.object(
                self.cb,
                "google_maps",
                new=AsyncMock(
                    return_value=(
                        "Ballarat VIC 3350, Australia",
                        -37.5621587,
                        143.8502556,
                        "3350",
                        "place-123",
                    )
                ),
            ),
            patch.object(
                self.cb, "openweather", new=AsyncMock(return_value={"daily": []})
            ) as openweather,
            patch.object(
                self.cb,
                "format_forecast_results",
                new=AsyncMock(return_value="Forecast output"),
            ) as format_forecast,
        ):
            self.assertResponse("weather --forecast Ballarat VIC AU", "Forecast output")

        openweather.assert_awaited_once_with(-37.5621587, 143.8502556)
        format_forecast.assert_awaited_once_with(
            "Ballarat VIC 3350, Australia", {"daily": []}
        )

    def test_weather_uses_saved_location_for_user_option(self):
        self.cb.db["friend@example.test"] = "ballarat vic au"

        with (
            patch.object(
                self.cb, "registryValue", side_effect=self._enabled_registry_value
            ),
            patch.object(
                self.irc.state,
                "nickToHostmask",
                return_value="Friend!friend@example.test",
            ),
            patch.object(
                self.cb,
                "google_maps",
                new=AsyncMock(
                    return_value=(
                        "Ballarat VIC 3350, Australia",
                        -37.5621587,
                        143.8502556,
                        "3350",
                        "place-123",
                    )
                ),
            ) as google_maps,
            patch.object(
                self.cb, "openweather", new=AsyncMock(return_value={"current": {}})
            ),
            patch.object(
                self.cb,
                "format_weather_results",
                new=AsyncMock(return_value="Saved weather output"),
            ),
        ):
            self.assertResponse("weather --user Friend", "Saved weather output")

        google_maps.assert_awaited_once_with("ballarat vic au")


class WeatherSmokeTestCase(unittest.TestCase):
    def test_plugin_module_exports_class(self):
        from . import plugin

        self.assertTrue(hasattr(plugin, "Class"))


class WeatherConcurrencyTestCase(unittest.TestCase):
    def test_threadsafe_runner_handles_parallel_calls(self):
        from . import plugin

        weather = plugin.Weather.__new__(plugin.Weather)
        weather._loop = asyncio.new_event_loop()
        weather._loop_thread = threading.Thread(
            target=weather._run_loop, name="WeatherTestLoop", daemon=True
        )
        weather._loop_thread.start()

        try:

            def run_task(i: int) -> int:
                return weather._run_coro_threadsafe(
                    asyncio.sleep(0.01, result=i), timeout=3
                )

            with ThreadPoolExecutor(max_workers=8) as executor:
                results = list(executor.map(run_task, range(24)))

            self.assertEqual(sorted(results), list(range(24)))
        finally:
            weather._loop.call_soon_threadsafe(weather._loop.stop)
            weather._loop_thread.join(timeout=3)
            self.assertFalse(
                weather._loop_thread.is_alive(), "Weather test loop thread did not stop"
            )
            weather._loop.close()

    def test_threadsafe_runner_timeout_cancels_and_recovers(self):
        from . import plugin

        weather = plugin.Weather.__new__(plugin.Weather)
        weather._loop = asyncio.new_event_loop()
        weather._loop_thread = threading.Thread(
            target=weather._run_loop, name="WeatherTestLoopTimeout", daemon=True
        )
        weather._loop_thread.start()

        try:
            with self.assertRaises(RuntimeError) as cm:
                weather._run_coro_threadsafe(asyncio.sleep(2, result="slow"), timeout=1)

            self.assertIn("Timed out", str(cm.exception))

            # The loop should remain usable after a timed-out/cancelled task.
            result = weather._run_coro_threadsafe(
                asyncio.sleep(0, result="ok"), timeout=1
            )
            self.assertEqual(result, "ok")
        finally:
            weather._loop.call_soon_threadsafe(weather._loop.stop)
            weather._loop_thread.join(timeout=3)
            self.assertFalse(
                weather._loop_thread.is_alive(), "Weather test loop thread did not stop"
            )
            weather._loop.close()


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
