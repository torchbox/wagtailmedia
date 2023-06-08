from django.forms.widgets import Widget
from wagtailmedia.forms import BaseMediaForm


class OverridenWidget(Widget):
    pass


class AlternateMediaForm(BaseMediaForm):
    class Meta:
        widgets = {
            "tags": OverridenWidget,
            "file": OverridenWidget,
            "thumbnail": OverridenWidget,
        }
