from django import VERSION as DJANGO_VERSION

from .version import __version__  # noqa


if DJANGO_VERSION >= (3, 2):
    # The declaration is only needed for older Django versions
    pass
else:
    default_app_config = "wagtailmedia.apps.WagtailMediaAppConfig"
