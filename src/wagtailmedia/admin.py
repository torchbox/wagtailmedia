from django.contrib import admin

from wagtailmedia.settings import wagtailmedia_settings


if wagtailmedia_settings.MEDIA_MODEL == "wagtailmedia.Media":
    # Only expose the package-provided media class in the Django admin if the installation
    # does not provide its own custom media class in order to avoid confusion.
    from wagtailmedia.models import Media

    admin.site.register(Media)
