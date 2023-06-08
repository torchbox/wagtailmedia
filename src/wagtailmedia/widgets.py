import json

from django import forms
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin.staticfiles import versioned_static
from wagtail.admin.widgets import BaseChooser, BaseChooserAdapter
from wagtail.telepath import register

from wagtailmedia.models import get_media_model


class AdminMediaChooser(BaseChooser):
    media_type = None
    choose_one_text = _("Choose a media item")
    choose_another_text = _("Choose another media item")
    link_to_chosen_text = _("Edit this media item")
    icon = "media"
    classname = "media-chooser"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = get_media_model()

    @property
    def chooser_modal_url_name(self):
        if self.media_type:
            return "wagtailmedia:chooser_typed"
        return "wagtailmedia:chooser"

    def get_chooser_modal_url(self):
        if self.media_type:
            return reverse("wagtailmedia:chooser_typed", args=(self.media_type,))
        return reverse("wagtailmedia:chooser")

    def render_js_init(self, id_, name, value):
        return f"createMediaChooser({json.dumps(id_)});"

    @property
    def media(self):
        return forms.Media(
            js=[
                "wagtailmedia/js/tabs.js",
                "wagtailmedia/js/media-chooser-modal.js",
                "wagtailmedia/js/media-chooser.js",
            ]
        )


class AdminAudioChooser(AdminMediaChooser):
    media_type = "audio"
    icon = "wagtailmedia-audio"
    choose_one_text = _("Choose audio")
    choose_another_text = _("Choose another audio item")
    link_to_chosen_text = _("Edit this audio item")


class AdminVideoChooser(AdminMediaChooser):
    media_type = "video"
    icon = "wagtailmedia-video"
    choose_one_text = _("Choose video")
    choose_another_text = _("Choose another video")
    link_to_chosen_text = _("Edit this video")


class MediaChooserAdapter(BaseChooserAdapter):
    js_constructor = "wagtailmedia.MediaChooser"

    @cached_property
    def media(self):
        return forms.Media(
            js=[
                versioned_static("wagtailmedia/js/media-chooser-telepath.js"),
            ]
        )


register(MediaChooserAdapter(), AdminMediaChooser)
register(MediaChooserAdapter(), AdminAudioChooser)
register(MediaChooserAdapter(), AdminVideoChooser)
