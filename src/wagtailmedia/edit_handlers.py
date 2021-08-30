from __future__ import absolute_import, unicode_literals

from wagtail.admin.edit_handlers import BaseChooserPanel

from wagtailmedia.widgets import AdminMediaChooser


class MediaChooserPanel(BaseChooserPanel):
    object_type_name = "media"

    def widget_overrides(self):
        return {self.field_name: AdminMediaChooser}
