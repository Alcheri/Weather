<!-- A fully asynchronous Weather plugin for Limnoria using the OpenWeather and Google Maps APIs. -->

# Weather

[![Tests][tests-badge]][tests-link]
[![Lint][lint-badge]][lint-link]
[![CodeQL][codeql-badge]][codeql-link]
![Python][python-badge]
![Black][black-badge]
![Limnoria][limnoria-badge]
![License][license-badge]

A fully asynchronous Limnoria plugin that uses the Google Maps Geocoding API
to resolve locations and the OpenWeather One Call 3.0 API to report current
conditions and forecasts.

All output is in metric units.

## Requirements

- Python 3.9 or newer
- `aiohttp`
- A Google Maps Geocoding API key
- An OpenWeather One Call 3.0 API key

Install the plugin dependency from the plugin directory:

```bash
python -m pip install --upgrade -r requirements.txt
```

## Installation

Clone the plugin into your Limnoria plugins directory, then load it in
Limnoria:

```text
/msg bot load Weather
```

## Configuration

Set the required API keys:

```text
/msg bot config plugins.Weather.googlemapsAPI <google-maps-api-key>
/msg bot config plugins.Weather.openweatherAPI <openweather-api-key>
```

Enable the plugin per channel:

```text
/msg bot config channel #channel plugins.Weather.enabled True
```

If the channel-scoped `enabled` value is `False`, the `weather` command does
not reply in that channel.

## Commands

### `weather [--user <nick>] [--forecast] [-- <location>]`

Shows current weather for a supplied location. If `<location>` is omitted, the
plugin looks up a saved location for the caller's `ident@host`. With
`--user <nick>`, it looks up the saved location for that nick's hostmask.

Use `--forecast` to return a five-day forecast instead of current conditions.

Examples:

```text
@weather Ballarat VIC AU
@weather --forecast Ballarat VIC AU
@weather --user SomeNick
@weather -- -37.5621587 143.8502556
```

The `--` separator is important when the location starts with a minus sign,
such as southern latitudes.

### `set <location>`

Stores a default location for your current `ident@host`.

Example:

```text
@set Ballarat VIC AU
```

### `unset`

Removes the saved default location for your current `ident@host`.

Example:

```text
@unset
```

### `google <location>`

Resolves a location through Google Maps and returns the formatted address,
postcode when available, Google place ID, latitude, and longitude.

Examples:

```text
@google Ballarat VIC AU
@google -37.5283674, 143.8164991
```

## Notes

- Country codes should use ISO 3166-1 alpha-2 codes where applicable.
- Saved locations are stored per `ident@host`.
- The plugin keeps its own async event loop and HTTP session so Limnoria
  commands can remain synchronous from the user's point of view.

## Development

From the plugin directory:

```bash
python -m ruff check .
python -m black --check .
python -m pytest
```

<!-- Badge reference definitions -->
[tests-badge]: https://github.com/Alcheri/Weather/actions/workflows/tests.yml/badge.svg
[tests-link]: https://github.com/Alcheri/Weather/actions/workflows/tests.yml

[lint-badge]: https://github.com/Alcheri/Weather/actions/workflows/lint.yml/badge.svg
[lint-link]: https://github.com/Alcheri/Weather/actions/workflows/lint.yml

[codeql-badge]: https://github.com/Alcheri/Weather/actions/workflows/codeql.yml/badge.svg
[codeql-link]: https://github.com/Alcheri/Weather/security/code-scanning

[python-badge]: https://img.shields.io/badge/python-3.9%2B-blue.svg
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[limnoria-badge]: https://img.shields.io/badge/limnoria-compatible-brightgreen.svg
[license-badge]: https://img.shields.io/badge/License-BSD_3--Clause-blue.svg

