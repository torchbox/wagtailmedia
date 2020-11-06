from __future__ import absolute_import, unicode_literals

import json

from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from wagtail.admin.widgets import AdminChooser

from wagtailmedia.models import get_media_model


class AdminMediaChooser(AdminChooser):
    choose_one_text = _("Choose a media item")
    choose_another_text = _("Choose another media item")
    link_to_chosen_text = _("Edit this media item")

    def __init__(self, **kwargs):
        super(AdminMediaChooser, self).__init__(**kwargs)
        self.media_model = get_media_model()

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
