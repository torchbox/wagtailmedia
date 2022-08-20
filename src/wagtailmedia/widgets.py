from __future__ import absolute_import, unicode_literals

import json

from django import forms
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from wagtail.admin.staticfiles import versioned_static
from wagtail.admin.widgets import AdminChooser
from wagtail.utils.version import get_main_version


try:
    from wagtail.telepath import register
    from wagtail.widget_adapters import WidgetAdapter
except ImportError:
    from wagtail.core.telepath import register
    from wagtail.core.widget_adapters import WidgetAdapter

from wagtailmedia.models import get_media_model


class AdminMediaChooser(AdminChooser):
    media_type = None
    choose_one_text = _("Choose a media item")
    choose_another_text = _("Choose another media item")
    link_to_chosen_text = _("Edit this media item")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.media_model = get_media_model()

    def get_value_data(self, value):
        if value is None:
            return value
        if not isinstance(value, self.media_model):
            value = self.media_model.objects.get(pk=value)
        return {
            "id": value.pk,
            "title": value.title,
            "edit_link": reverse("wagtailmedia:edit", args=[value.pk]),
        }

    def render_html(self, name, value, attrs):
        value_data = value if value is not None else {}

        original_field_html = super().render_html(name, value_data.get("id"), attrs)

        if self.media_type:
            chooser_url = reverse("wagtailmedia:chooser_typed", args=(self.media_type,))
        else:
            chooser_url = reverse("wagtailmedia:chooser")

        return render_to_string(
            "wagtailmedia/widgets/media_chooser.html",
            {
                "widget": self,
                "original_field_html": original_field_html,
                "attrs": attrs,
                "value": value_data != {},  # only used to identify blank values
                "title": value_data.get("title", ""),
                "edit_url": value_data.get("edit_link", ""),
                "chooser_url": chooser_url,
                "wagtail_version": get_main_version(),
            },
        )

    def render_js_init(self, id_, name, value):
        return "createMediaChooser({0});".format(json.dumps(id_))

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
    choose_one_text = _("Choose audio")
    choose_another_text = _("Choose another audio item")
    link_to_chosen_text = _("Edit this audio item")


class AdminVideoChooser(AdminMediaChooser):
    media_type = "video"
    choose_one_text = _("Choose video")
    choose_another_text = _("Choose another video")
    link_to_chosen_text = _("Edit this video")


class MediaChooserAdapter(WidgetAdapter):
    js_constructor = "wagtailmedia.MediaChooser"

    def js_args(self, widget):
        return [
            widget.render_html("__NAME__", None, attrs={"id": "__ID__"}),
            widget.id_for_label("__ID__"),
        ]

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
