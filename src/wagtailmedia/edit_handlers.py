from __future__ import absolute_import, unicode_literals

from wagtail.admin.edit_handlers import BaseChooserPanel

from wagtailmedia.widgets import AdminAudioChooser, AdminMediaChooser, AdminVideoChooser


class MediaChooserPanel(BaseChooserPanel):
    object_type_name = "media"

    def __init__(self, field_name, media_type=None, *args, **kwargs):
        super().__init__(field_name=field_name, *args, **kwargs)

        self.media_type = media_type

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs.update(media_type=self.media_type)
        return kwargs

    def widget_overrides(self):
        if self.media_type == "audio":
            widget_class = AdminAudioChooser
        elif self.media_type == "video":
            widget_class = AdminVideoChooser
        else:
            widget_class = AdminMediaChooser

        return {self.field_name: widget_class}
