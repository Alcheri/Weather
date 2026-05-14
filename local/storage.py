###
# Copyright © 2017 - 2026, Barry Suridge
# All rights reserved.
#
###

import json

from supybot import log


class WeatherLocationStore:
    """Persist saved weather locations by ident@host."""

    def __init__(self, filename: str):
        self.filename = filename
        self.data: dict[str, str] = {}

    def load(self) -> dict[str, str]:
        try:
            with open(self.filename, "r", encoding="utf-8") as handle:
                self.data = json.load(handle)
        except FileNotFoundError:
            self.data = {}
        except json.JSONDecodeError as error:
            log.warning(f"Failed to parse the database file: {error}")
            self.data = {}
        except Exception as error:
            log.warning(f"Unable to load database: {error}")
            self.data = {}
        return self.data

    def flush(self) -> None:
        try:
            with open(self.filename, "w", encoding="utf-8") as handle:
                json.dump(self.data, handle, indent=4)
        except Exception as error:
            log.warning(f"Unable to save database: {error}")

    def get(self, ident_host: str) -> str:
        return self.data[ident_host]

    def set(self, ident_host: str, location: str) -> None:
        self.data[ident_host] = location.lower()

    def unset(self, ident_host: str) -> bool:
        if ident_host in self.data:
            del self.data[ident_host]
            return True
        return False
