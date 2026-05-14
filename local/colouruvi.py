###
# Copyright © 2017 - 2026, Barry Suridge
# All rights reserved.
#
###

from supybot import ircutils


class UVI:
    """Hello, I am the UV Index meter!"""

    # adapted from https://en.wikipedia.org/wiki/Ultraviolet_index#Index_usage
    @staticmethod
    def colour_uvi(uvi: float) -> str:
        """
        Assigns a descriptive text and colour to the UV Index value.
        """
        # Define ranges, colours, and descriptions
        ranges = [
            (0, 3, "light green", "Low"),
            (3, 6, "yellow", "Moderate"),
            (6, 8, "orange", "High"),
            (8, 11, "red", "Very High"),
            (11, float("inf"), "purple", "Extreme"),
        ]

        # Handle invalid values
        if uvi < 0:
            return ircutils.mircColor("Unknown UVI", "light grey")

        # Match the UV index to a range and return coloured text with description
        for lower, upper, colour, description in ranges:
            if lower <= uvi < upper:
                return ircutils.mircColor(f"UVI {uvi} ({description})", colour)

        # Fallback (should not happen)
        return ircutils.mircColor("UVI Unknown", "grey")
