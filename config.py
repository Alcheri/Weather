# Copyright © 2017 - 2026, Barry Suridge
# All rights reserved.
#
#
###

from supybot import conf, registry

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("Weather")
except ImportError:

    def _(text):
        return text


def configure(advanced):
    conf.registerPlugin("Weather", True)


Weather = conf.registerPlugin("Weather")

conf.registerGlobalValue(
    Weather,
    "googlemapsAPI",
    registry.String("", _("""Sets the API key for Google Maps."""), private=True),
)

conf.registerGlobalValue(
    Weather,
    "openweatherAPI",
    registry.String("", _("""Sets the API key for Open Weather."""), private=True),
)

conf.registerChannelValue(
    Weather,
    "enabled",
    registry.Boolean(False, """Should plugin work in this channel?"""),
)

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
