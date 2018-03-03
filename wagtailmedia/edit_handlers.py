from __future__ import absolute_import, unicode_literals

try:
    from wagtail.admin.edit_handlers import BaseChooserPanel
except ImportError:
    from wagtail.wagtailadmin.edit_handlers import BaseChooserPanel

from wagtailmedia.widgets import AdminMediaChooser


class BaseMediaChooserPanel(BaseChooserPanel):
    object_type_name = 'media'

    @classmethod
    def widget_overrides(cls):
        return {cls.field_name: AdminMediaChooser}


class MediaChooserPanel(object):
    def __init__(self, field_name):
        self.field_name = field_name

    def bind_to_model(self, model):
        return type(str('_MediaChooserPanel'), (BaseMediaChooserPanel,), {
            'model': model,
            'field_name': self.field_name,
        })
