"""
The wagtailmedia settings are namespaced in the WAGTAILMEDIA setting.
For example your project's `settings.py` file might look like this:
WAGTAILMEDIA = {
    "MEDIA_MODEL": "mymedia.CustomMedia",
    # ...
}
This module provides the `wagtailmedia_settings` object, that is used to access
the settings. It checks for user settings first, with fallback to defaults.
"""

import warnings

from django.conf import settings
from django.test.signals import setting_changed


DEFAULTS = {
    "MEDIA_MODEL": "wagtailmedia.Media",
    "MEDIA_FORM_BASE": "",
    "AUDIO_EXTENSIONS": ["aac", "aiff", "flac", "m4a", "m4b", "mp3", "ogg", "wav"],
    "VIDEO_EXTENSIONS": [
        "avi",
        "h264",
        "m4v",
        "mkv",
        "mov",
        "mp4",
        "mpeg",
        "mpg",
        "ogv",
        "webm",
    ],
}

# List of settings that have been deprecated
DEPRECATED_SETTINGS = []

# List of settings that have been removed
# note: use a tuple of (setting, deprecation warning from deprecation.py)
REMOVED_SETTINGS = []


class WagtailMediaSettings:
    """
    A settings object that allows the wagtailmedia settings to be accessed as
    properties. For example:
        from wagtailmedia.settings import wagtailmedia_settings
        print(wagtailmedia_settings.MEDIA_MODEL)
    Note:
    This is an internal class that is only compatible with settings namespaced
    under the WAGTAILMEDIA name. It is not intended to be used by 3rd-party
    apps, and test helpers like `override_settings` may not work as expected.
    """

    def __init__(self, user_settings=None, defaults=None):
        if user_settings:
            self._user_settings = self.__check_user_settings(user_settings)
        self.defaults = defaults or DEFAULTS
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = self.__check_user_settings(
                getattr(settings, "WAGTAILMEDIA", {})
            )
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError(f"Invalid wagtailmedia setting: '{attr}'")

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def __check_user_settings(self, user_settings):
        for setting, category in DEPRECATED_SETTINGS:
            if setting in user_settings or hasattr(settings, setting):
                new_setting = setting.replace("WAGTAILMEDIA_", "")
                warnings.warn(
                    f"The '{setting}' setting is deprecated and will be removed in the next release, "
                    f'use WAGTAILMEDIA["{new_setting}"] instead.',
                    category=category,
                    stacklevel=2,
                )
                user_settings[new_setting] = user_settings[setting]
        for setting in REMOVED_SETTINGS:
            if setting in user_settings:
                raise RuntimeError(
                    f"The '{setting}' setting has been removed. "
                    f"Please refer to the wagtailmedia documentation for available settings."
                )
        return user_settings

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")


wagtailmedia_settings = WagtailMediaSettings(None, DEFAULTS)


def reload_wagtailmedia_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == "WAGTAILMEDIA":
        wagtailmedia_settings.reload()


setting_changed.connect(reload_wagtailmedia_settings)
