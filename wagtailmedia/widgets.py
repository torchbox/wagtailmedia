from __future__ import absolute_import, unicode_literals

import json

from django import forms
from django.urls import reverse
from django.utils.functional import cached_property
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from wagtail.admin.widgets import AdminChooser

from wagtail import VERSION as WAGTAIL_VERSION

if WAGTAIL_VERSION > (2, 13):
    from wagtail.core.telepath import register
    from wagtail.admin.staticfiles import versioned_static
    from wagtail.core.widget_adapters import WidgetAdapter

from wagtailmedia.models import get_media_model


class AdminMediaChooser(AdminChooser):
    choose_one_text = _("Choose a media item")
    choose_another_text = _("Choose another media item")
    link_to_chosen_text = _("Edit this media item")

    def __init__(self, **kwargs):
        super(AdminMediaChooser, self).__init__(**kwargs)
        self.media_model = get_media_model()

    def get_value_data(self, value):
        if not WAGTAIL_VERSION > (2, 13):
            return super().get_value_data(value)
        if value is None:
            return value
        if not isinstance(value, self.media_model):
            value = self.media_model.objects.get(pk=value)
        return {
            "id": value.pk,
            "title": value.title,
            "edit_link": reverse("wagtailmedia:edit", args=[value.id]),
        }

    def render_html(self, name, value, attrs):
        instance, value = self.get_instance_and_id(self.media_model, value)
        original_field_html = super(AdminMediaChooser, self).render_html(
            name, value, attrs
        )

        return render_to_string(
            "wagtailmedia/widgets/media_chooser.html",
            {
                "widget": self,
                "original_field_html": original_field_html,
                "attrs": attrs,
                "value": value,
                "media": instance,
            },
        )

    def render_js_init(self, id_, name, value):
        return "createMediaChooser({0});".format(json.dumps(id_))

    class Media:
        js = [
            "wagtailmedia/js/media-chooser-modal.js",
            "wagtailmedia/js/media-chooser.js",
        ]


if WAGTAIL_VERSION > (2, 13):

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
                js=[versioned_static("wagtailmedia/js/media-chooser-telepath.js"),]
            )

    register(MediaChooserAdapter(), AdminMediaChooser)
