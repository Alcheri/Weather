<!-- A fully asynchronous Weather plugin for Limnoria using the OpenWeather and Google Maps APIs. -->

<h1 align="center">Weather</h1>

<!-- README_HEADER:start -->
<p align="center">
  <a href="https://github.com/Alcheri/Weather/actions/workflows/tests.yml">
    <img src="https://github.com/Alcheri/Weather/actions/workflows/tests.yml/badge.svg" alt="Tests">
  </a>
  <a href="https://github.com/Alcheri/Weather/actions/workflows/lint.yml">
    <img src="https://github.com/Alcheri/Weather/actions/workflows/lint.yml/badge.svg" alt="Lint">
  </a>
  <a href="https://github.com/Alcheri/Weather/security/code-scanning">
    <img src="https://github.com/Alcheri/Weather/actions/workflows/codeql.yml/badge.svg" alt="CodeQL">
  </a>
  <img src="https://img.shields.io/badge/python-3.9%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black">
  <img src="https://img.shields.io/badge/limnoria-compatible-brightgreen.svg" alt="Limnoria">
  <img src="https://img.shields.io/badge/License-BSD_3--Clause-blue.svg" alt="License">
</p>
<!-- README_HEADER:end -->

<p align="center">
  <em>A fully asynchronous Weather plugin for Limnoria using the OpenWeather and Google Maps APIs.</em>
</p>

All output is in [Metric](https://www.bipm.org/en/)

This plugin uses Alpha-2 Code for country code [iso.org](https://www.iso.org/obp/ui#iso:pub:PUB500001:en)

## Setting up

OpenWeather One Call 3.0 API gathers data requiring a (free? )subscription.\
Subscription: [One Call API 3.0](https://openweathermap.org/api/one-call-3)

Google Maps API gathers data requiring a (free?) subscription.\
Subscription: [Google Maps API](https://developers.google.com/maps)

**Google** gives each Google Maps account $200/month of free credit, equivalent to 40,000 addresses geocoded per month.

## Install

Go into your Limnoria plugin dir, usually ~/runbot/plugins and run:

```plaintext
git clone https://github.com/Alcheri/Weather.git
```

To install additional requirements, run from /plugins/Weather folder:

```plaintext
pip install --upgrade -r requirements.txt 
```

Next, load the plugin:

```plaintext
/msg bot load Weather
```

## Configure your bot

* **_config plugins.Weather.openweatherAPI [your_key_here]_**
* **_config plugins.Weather.googlemapsAPI [your_key_here]_**
* **_config channel #channel plugins.Weather.enabled True or False (On or Off)_**

**Note:** For all Southern Hemisphere latitudes prefix the argument with '--' i.e.:
<pre>   -- -37.5621587 143.8502556</pre>

## Using
<!-- LaTeX text formatting (colour) -->
>\<Barry\> @weather 1600 Amphitheatre Pkwy, Mountain View, CA\
>\<Borg\>  1600 Amphitheatre Pkwy, Mountain View, CA 94043, USA (Lat: 122°5' 7.08" W, Lon: 37°25' 19.56" N) | Clear sky, Temp: ${\texttt{\color{green}18.0°C}}$, Feels like: ${\texttt{\color{green}17.0°C}}$, Humidity: 33%, Clouds: 0%, Wind: 22 Km/h N, ${\texttt{\color{green}UVI 1 (Low)}}$
>
>\<Barry\> @weather -- -37.5621587 143.8502556\
>\<Borg\>  Ballarat Central VIC 3350, Australia (Lat: 143°51' 1.08" E, Lon: 37°33' 43.92" S) | Clear sky, Temp: ${\texttt{\color{yellow}24.0°C}}$, Feels like: ${\texttt{\color{yellow}23.0°C }}$, Humidity: 99%, Clouds: 9%, Wind: 5 Km/h SSE, ${\texttt{\color{red}UVI 9 (Very High)}}$

```plaintext
<Barry> @google -37.5283674, 143.8164991
<Borg>  From Google Maps: 1275 Grevillea Rd, Wendouree VIC 3355, Australia 3355 [ID: ChIJcSzC6YxD0WoRWtgRRJh8D2U] -37.5283674 143.8164991

<Barry> @google Ballarat VIC AU
<Borg>  From Google Maps: Ballarat VIC, Australia N/A [ID: ChIJeRiTMFRE0WoRILegMKR5BQQ] -37.5621587 143.8502556

@weather set [location] -- Sets your current ident@host to [location]

@weather unset -- Removes your current ident@host

@weather help -- Plugin help - accepts no arguments.
```

## Diagram Notes

Some Chromium-based Markdown previewers may not render Mermaid diagrams
correctly. A PNG render of the flowchart is included for compatibility.

The Mermaid source remains available for editing.

<br/><br/>
<p align="center">Copyright © MMXXVI, Barry Suridge</p>
