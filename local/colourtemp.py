###
# Copyright © 2017 - 2026, Barry Suridge
# All rights reserved.
#
###

from supybot import ircutils

# Constants
APOSTROPHE = "\N{APOSTROPHE}"
DEGREE_SIGN = "\N{DEGREE SIGN}"
PERCENT_SIGN = "\N{PERCENT SIGN}"
QUOTATION_MARK = "\N{QUOTATION MARK}"


class COLTEMP:
    """Colourise temperatures."""

    @staticmethod
    def colour_temperature(celsius: float) -> str:
        """
        Colourise and format temperatures.
        """
        # Define ranges, colours, and descriptions
        ranges = [
            (float("-inf"), 0, "blue"),  # Below 0°C
            (0, 1, "teal"),  # Exactly 0°C
            (1, 10, "light blue"),  # 1°C to < 10°C
            (10, 20, "light green"),  # 10°C to < 20°C
            (20, 30, "yellow"),  # 20°C to < 30°C
            (30, 40, "orange"),  # 30°C to < 40°C
            (40, float("inf"), "red"),  # 40°C and above
        ]

        # Ensure the input is a float
        c = float(celsius)

        # Match the temperature to a range and colour it
        for lower, upper, colour in ranges:
            if lower <= c < upper:
                formatted_temp = f"{c}{DEGREE_SIGN}C"
                return ircutils.mircColor(formatted_temp, colour)

        # Fallback (should not happen)
        return ircutils.mircColor(f"{c}{DEGREE_SIGN}C", "grey")
