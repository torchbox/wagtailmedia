from django import forms
from django.test import TestCase, override_settings
from wagtail.admin import widgets

from tests.testapp.forms import AlternateMediaForm, OverridenWidget
from wagtailmedia import models
from wagtailmedia.forms import BaseMediaForm, get_media_base_form, get_media_form


class TestFormOverride(TestCase):
    def test_get_media_base_form(self):
        self.assertIs(get_media_base_form(), BaseMediaForm)

    def test_get_media_form(self):
        bases = get_media_form(models.Media).__bases__
        self.assertIn(BaseMediaForm, bases)
        self.assertNotIn(AlternateMediaForm, bases)

    def test_get_media_form_widgets(self):
        Form = get_media_form(models.Media)
        form = Form()
        self.assertIsInstance(form.fields["tags"].widget, widgets.AdminTagWidget)
        self.assertIsInstance(form.fields["file"].widget, forms.FileInput)
        self.assertIsInstance(form.fields["thumbnail"].widget, forms.ClearableFileInput)

    @override_settings(
        WAGTAILMEDIA={"MEDIA_FORM_BASE": "tests.testapp.forms.AlternateMediaForm"}
    )
    def test_overridden_base_form(self):
        self.assertIs(get_media_base_form(), AlternateMediaForm)

    @override_settings(
        WAGTAILMEDIA={"MEDIA_FORM_BASE": "tests.testapp.forms.AlternateMediaForm"}
    )
    def test_get_overridden_media_form(self):
        bases = get_media_form(models.Media).__bases__
        self.assertNotIn(BaseMediaForm, bases)
        self.assertIn(AlternateMediaForm, bases)

    @override_settings(
        WAGTAILMEDIA={"MEDIA_FORM_BASE": "tests.testapp.forms.AlternateMediaForm"}
    )
    def test_get_overridden_media_form_widgets(self):
        Form = get_media_form(models.Media)
        form = Form()
        self.assertIsInstance(form.fields["tags"].widget, OverridenWidget)
        self.assertIsInstance(form.fields["file"].widget, OverridenWidget)
        self.assertIsInstance(form.fields["thumbnail"].widget, OverridenWidget)
