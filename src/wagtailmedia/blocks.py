from __future__ import unicode_literals

from django.forms import ModelChoiceField
from django.forms.utils import flatatt
from django.utils.functional import cached_property
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext_lazy as _

from wagtail.core.blocks import ChooserBlock


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
    def widget(self):
        from wagtailmedia.widgets import AdminAudioChooser

        return AdminAudioChooser()

    def render_basic(self, value, context=None):
        if not value:
            return ""

        if value.type != self.media_type:
            return ""

        return format_html(
            "<audio controls>\n{sources}\n<p>{fallback}</p>\n</audio>",
            sources=format_html_join(
                "\n", "<source{0}>", [[flatatt(s)] for s in value.sources]
            ),
            fallback=_("Your browser does not support the audio element."),
        )


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
    def widget(self):
        from wagtailmedia.widgets import AdminVideoChooser

        return AdminVideoChooser()

    def render_basic(self, value, context=None):
        if not value:
            return ""

        if value.type != self.media_type:
            return ""

        return format_html(
            "<video controls>\n{sources}\n<p>{fallback}</p>\n</video>",
            sources=format_html_join(
                "\n", "<source{0}>", [[flatatt(s)] for s in value.sources]
            ),
            fallback=_("Your browser does not support the video element."),
        )
