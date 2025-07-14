from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from wagtail.admin.widgets import BaseChooser

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
