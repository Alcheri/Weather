# -*- coding: utf-8 -*-
###
# Copyright (c) 2017 - 2026, Barry Suridge
# All rights reserved.
###

import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
import unittest

import supybot.test as supybot_test


class WeatherTestCase(supybot_test.PluginTestCase):
    # Keep this for Limnoria's native plugin test harness; pytest should ignore it.
    __test__ = False
    plugins = ("Weather",)


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
