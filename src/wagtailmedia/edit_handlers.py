from __future__ import absolute_import, annotations, unicode_literals

from typing import TYPE_CHECKING, Optional, Type

from django.template.loader import render_to_string

from wagtail import VERSION as WAGTAIL_VERSION
from wagtail.admin.compare import ForeignObjectComparison

from .models import MediaType
from .utils import format_audio_html, format_video_html
from .widgets import AdminAudioChooser, AdminMediaChooser, AdminVideoChooser


if WAGTAIL_VERSION >= (3, 0):
    from wagtail.admin.panels import FieldPanel
else:
    from wagtail.admin.edit_handlers import BaseChooserPanel as FieldPanel

if TYPE_CHECKING:
    from .models import AbstractMedia


class MediaChooserPanel(FieldPanel):
    object_type_name = "media"

    def __init__(self, field_name, media_type=None, *args, **kwargs):
        super().__init__(field_name=field_name, *args, **kwargs)

        self.media_type = media_type

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs.update(media_type=self.media_type)
        return kwargs

    @property
    def _widget_class(self):
        if self.media_type == "audio":
            return AdminAudioChooser
        elif self.media_type == "video":
            return AdminVideoChooser
        return AdminMediaChooser

    if WAGTAIL_VERSION >= (3, 0):

        def get_form_options(self) -> dict:
            opts = super().get_form_options()
            if "widgets" in opts:
                opts["widgets"][self.field_name] = self._widget_class
            else:
                opts["widgets"] = {self.field_name: self._widget_class}

            return opts

    else:

        def widget_overrides(self) -> dict:
            return {self.field_name: self._widget_class}

        def get_comparison_class(self) -> Optional[Type[MediaFieldComparison]]:
            comparison_class = super().get_comparison_class()
            if comparison_class is None:
                return

            return MediaFieldComparison


class MediaFieldComparison(ForeignObjectComparison):
    def htmldiff(self) -> str:
        media_item_a, media_item_b = self.get_objects()
        if not all([media_item_a, media_item_b]):
            return ""

        return render_to_string(
            "wagtailmedia/widgets/compare.html",
            {
                "media_item_a": self.render_media_item(media_item_a),
                "media_item_b": self.render_media_item(media_item_b),
            },
        )

    @staticmethod
    def render_media_item(item: AbstractMedia) -> str:
        if item.type == MediaType.AUDIO:
            return format_audio_html(item)
        else:
            return format_video_html(item)
