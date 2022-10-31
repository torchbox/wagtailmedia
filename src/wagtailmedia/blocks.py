from __future__ import unicode_literals

from typing import TYPE_CHECKING, Type

from django.forms import ModelChoiceField
from django.template.loader import render_to_string
from django.utils.functional import cached_property

from wagtail.admin.compare import BlockComparison
from wagtail.core.blocks import ChooserBlock

from .utils import format_audio_html, format_video_html


if TYPE_CHECKING:
    from .widgets import AdminAudioChooser, AdminVideoChooser


class AbstractMediaChooserBlock(ChooserBlock):
    def __init__(
        self, required=True, help_text=None, validators=(), media_type=None, **kwargs
    ):
        super().__init__(
            required=required, help_text=help_text, validators=validators, **kwargs
        )
        self.media_type = media_type

    @cached_property
    def target_model(self):
        from wagtailmedia.models import get_media_model

        return get_media_model()

    @cached_property
    def field(self):
        if not self.media_type:
            return super().field

        return ModelChoiceField(
            queryset=self.target_model.objects.filter(type=self.media_type),
            widget=self.widget,
            required=self._required,
            validators=self._validators,
            help_text=self._help_text,
        )

    @cached_property
    def widget(self):
        from wagtailmedia.widgets import AdminMediaChooser

        return AdminMediaChooser()

    def get_form_state(self, value):
        return self.widget.get_value_data(value)

    def render_basic(self, value, context=None):
        raise NotImplementedError(
            "You need to implement %s.render_basic" % self.__class__.__name__
        )

    def get_comparison_class(self) -> Type["MediaChooserBlockComparison"]:
        return MediaChooserBlockComparison


class MediaChooserBlockComparison(BlockComparison):
    def htmlvalue(self, value) -> str:
        return render_to_string(
            "wagtailmedia/widgets/compare.html",
            {
                "media_item_a": self.block.render_basic(value),
                "media_item_b": self.block.render_basic(value),
            },
        )

    def htmldiff(self) -> str:
        return render_to_string(
            "wagtailmedia/widgets/compare.html",
            {
                "media_item_a": self.block.render_basic(self.val_a),
                "media_item_b": self.block.render_basic(self.val_b),
            },
        )


class AudioChooserBlock(AbstractMediaChooserBlock):
    def __init__(self, required=True, help_text=None, validators=(), **kwargs):
        super().__init__(
            required=required,
            help_text=help_text,
            validators=validators,
            media_type="audio",
            **kwargs,
        )

    @cached_property
    def widget(self) -> "AdminAudioChooser":
        from wagtailmedia.widgets import AdminAudioChooser

        return AdminAudioChooser()

    def render_basic(self, value, context=None) -> str:
        if not value:
            return ""

        if value.type != self.media_type:
            return ""

        return format_audio_html(value)


class VideoChooserBlock(AbstractMediaChooserBlock):
    def __init__(self, required=True, help_text=None, validators=(), **kwargs):
        super().__init__(
            required=required,
            help_text=help_text,
            validators=validators,
            media_type="video",
            **kwargs,
        )

    @cached_property
    def widget(self) -> "AdminVideoChooser":
        from wagtailmedia.widgets import AdminVideoChooser

        return AdminVideoChooser()

    def render_basic(self, value, context=None) -> str:
        if not value:
            return ""

        if value.type != self.media_type:
            return ""

        return format_video_html(value)
