from __future__ import absolute_import, unicode_literals

from wagtailmedia.widgets import AdminMediaChooser

try:
    from wagtail.admin.edit_handlers import BaseChooserPanel
except ImportError:  # fallback for wagtail <2.0
    from wagtail.wagtailadmin.edit_handlers import BaseChooserPanel


#class BaseMediaChooserPanel(BaseChooserPanel):
class MediaChooserPanel(BaseChooserPanel):
    object_type_name = 'media'

#    @classmethod
    def widget_overrides(self):
        return {self.field_name: AdminMediaChooser}

    ##IDK IF THIS WORKS.
    #def bind_to_model(self, model):
    #    return type(str('_MediaChooserPanel'), (MediaChooserPanel,), {
    #        'model': model,
    #        'field_name': self.field_name,
    #    })


#class MediaChooserPanel(BaseMediaChooserPanel):
#    def __init__(self, field_name, heading='Choose Media', classname='inset', help_text='A panel to choose certain media', widget=AdminMediaChooser):
#        self.field_name = field_name
#        self.heading = heading
#        self.classname = classname
#        self.help_text = help_text
#        self.field_name = field_name
#
#    # This causes an error as written.
#    #def bind_to_model(self, model):
#    #    return type(str('_MediaChooserPanel'), (BaseMediaChooserPanel,), {
#    #        'model': model,
#    #        'field_name': self.field_name,
#    #    })
#class MediaChooserPanel(BaseMediaChooserPanel): def __init__(self, field_name): self.field_name = field_name def bind_to_model(self, model): new = self.clone() new.model = model new.on_model_bound() return new
