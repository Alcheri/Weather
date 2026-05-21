###
# Copyright © 2017 - 2026, Barry Suridge
# All rights reserved.
#
###

import json
import os
from pathlib import Path

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
        path = Path(self.filename)
        tmp_path = path.with_name(f".{path.name}.tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as handle:
                json.dump(self.data, handle, indent=4)
                handle.write("\n")
            os.replace(tmp_path, path)
        except Exception as error:
            log.warning(f"Unable to save database: {error}")
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass

    def get(self, ident_host: str) -> str:
        return self.data[ident_host]

    def set(self, ident_host: str, location: str) -> None:
        self.data[ident_host] = location.lower()

    def unset(self, ident_host: str) -> bool:
        if ident_host in self.data:
            del self.data[ident_host]
            return True
        return False
