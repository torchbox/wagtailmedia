from __future__ import absolute_import, unicode_literals

from wagtail import VERSION as WAGTAIL_VERSION

from wagtailmedia.widgets import AdminAudioChooser, AdminMediaChooser, AdminVideoChooser


if WAGTAIL_VERSION >= (3, 0):
    from wagtail.admin.panels import FieldPanel
else:
    from wagtail.admin.edit_handlers import BaseChooserPanel as FieldPanel


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

        def get_form_options(self):
            opts = super().get_form_options()
            if "widgets" in opts:
                opts["widgets"][self.field_name] = self._widget_class
            else:
                opts["widgets"] = {self.field_name: self._widget_class}

            return opts

    else:

        def widget_overrides(self):
            return {self.field_name: self._widget_class}
