# Changelog

All notable changes to the Weather plugin are documented here.

---

## [Unreleased] - 2026-03-27 to present

### Added

- CodeQL static analysis workflow (`.github/workflows/codeql.yml`).
- CodeQL and code-style badges in README.
- Dedicated async loop thread execution model (`_run_loop` + `_run_coro_threadsafe`) for thread-safe command handling.
- Pytest discovery config in `pyproject.toml` and pytest-compatible test harness integration.
- Concurrency regression tests for parallel task scheduling and timeout/cancellation recovery.

### Changed

- Packaging migrated from `setup.py` to PEP 621 `pyproject.toml`; `setup.py` removed.
- Dead per-request `ClientSession` code removed from `fetch_data()`.
- GitHub Actions CI workflows standardised (lint + tests).
- Redundant labeler config removed.
- README updated with PluginDownloader metadata entry.
- Runtime Python version gate fixed to correctly allow Python 3.9+.
- `requires-python` aligned with runtime requirement (`>=3.9`).
- Error handling and validation hardened for unavailable HTTP session and hostmask/location edge cases.

---

## [1.0.0] - 2026-03-25

### Added

- Persistent `aiohttp.ClientSession` created at plugin start and closed cleanly on `die()`,
  replacing per-request session creation.
- Dedicated `_create_session()` async helper and proper event-loop management
  via `asyncio.new_event_loop()`.
- `threaded = True` set on the plugin class to prevent blocking the bot.
- Explicit `encoding="utf-8"` on all file I/O (`load_db` / `flush_db`).
- Graceful session and event-loop teardown in `die()` with logged warnings on failure.
- Baseline test suite (`test.py`) with `WeatherTestCase` and `WeatherSmokeTestCase`.
- `Flowchart.mmd` and `Weather_Flowchart.png` architecture diagrams.

### Changed

- Plugin `__doc__` updated to document the `weather`, `weather --forecast`, and `set` commands.
- `fetch_data()` refactored to use the shared session; URL no longer leaked into error context.
- UV index source attribution updated from EPA to Australian Bureau of Meteorology (BOM).
- User-Agent header changed from a generic Firefox string to
  `Limnoria-Weather/1.0 (+https://github.com/Alcheri/Weather)`.
- Import error re-raised as `ImportError` instead of bare `Exception`.
- Python code formatted with `psf/black`.
- Line endings normalised to LF across all Python files via `.gitattributes`.

---

## [0.x] - 2025-01-07 to 2025-02-25

### Added

- Initial upload of plugin files: `plugin.py`, `config.py`, `__init__.py`,
  `requirements.txt`, `local/colourtemp.py`, `local/colouruvi.py`, `setup.py`.
- GitHub Actions workflows: Black auto-formatter, Pylint, and issue labeler.
- GitHub issue templates.
- `LICENCE.md` and `README.md`.

### Changed

- Minor code tweaks and `colourtemp.py` updates.
- `.gitignore` updated to exclude Python cache artefacts.
- README expanded with usage information and badges.
