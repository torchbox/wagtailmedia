from django.conf import settings
from django.contrib import admin

from wagtailmedia.models import Media


if (
    hasattr(settings, "WAGTAILMEDIA_MEDIA_MODEL")
    and settings.WAGTAILMEDIA_MEDIA_MODEL != "wagtailmedia.Media"
):
    # This installation provides its own custom media class;
    # to avoid confusion, we won't expose the unused wagtailmedia.Media class
    # in the admin.
    pass
else:
    admin.site.register(Media)
