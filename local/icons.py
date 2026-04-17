# -*- coding: utf-8 -*-
###
# Copyright © 2017 - 2026, Barry Suridge
# All rights reserved.
#
###


@staticmethod
def _get_status_icon(code):
    """Use the given code to display appropriate
    weather status icon"""
    switcher = {
        "01d": "☀",
        "01n": "🌚",
        "02d": "🌤",
        "02n": "🌚",
        "03d": "☁",
        "03n": "🌚",
        "04d": "☁",
        "04n": "🌚",
        "09d": "🌦",
        "09n": "🌚",
        "10d": "🌦",
        "10n": "🌚",
        "11d": "⛈",
        "11n": "⛈",
        "13d": "❄",
        "13n": "❄",
        "50d": "🌫",
        "50n": "🌫",
    }
    return switcher.get(code, "🤷")
