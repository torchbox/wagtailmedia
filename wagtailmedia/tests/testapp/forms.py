from django.forms import ModelForm
from django.forms.widgets import ClearableFileInput


class AlternateFileInput(ClearableFileInput):
    pass


class AlternateMediaForm(ModelForm):
    class Meta:
        widgets = {
            'file': AlternateFileInput
        }
