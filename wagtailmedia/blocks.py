from __future__ import unicode_literals

from django.utils.functional import cached_property
from django.utils.html import format_html

from wagtail.wagtailcore.blocks import ChooserBlock


class MediaChooserBlock(ChooserBlock):
    @cached_property
    def target_model(self):
        from wagtailmedia.models import get_media_model
        return get_media_model()

    @cached_property
    def widget(self):
        from wagtailmedia.widgets import AdminMediaChooser
        return AdminMediaChooser

    def render_basic(self, value):
        if value:
            return format_html('<a href="{0}">{1}</a>', value.url, value.title)
        else:
            return ''
