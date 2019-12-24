from django.forms import ModelForm
from django.forms.widgets import Widget


class OverridenWidget(Widget):
    pass


class AlternateMediaForm(ModelForm):
    class Meta:
        widgets = {
            'tags': OverridenWidget,
            'file': OverridenWidget,
            'thumbnail': OverridenWidget,
        }
