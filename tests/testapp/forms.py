from django import forms
from django.forms.widgets import Widget

from wagtailmedia.forms import BaseMediaForm


class OverridenWidget(Widget):
    pass


class AlternateMediaForm(BaseMediaForm):
    form_only_field = forms.DateTimeField()

    class Meta:
        widgets = {
            "tags": OverridenWidget,
            "file": OverridenWidget,
            "thumbnail": OverridenWidget,
        }
