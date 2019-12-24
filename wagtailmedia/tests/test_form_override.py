from unittest.mock import patch

from django.test import SimpleTestCase, override_settings
from wagtailmedia import models
from wagtailmedia.forms import BaseMediaForm, get_media_form, get_media_base_form, media_base_form
from wagtailmedia.tests.testapp.forms import AlternateMediaForm


class TestFormOverride(SimpleTestCase):
    def test_media_base_form(self):
        self.assertIs(media_base_form, BaseMediaForm)
    
    def test_get_media_base_form(self):
        self.assertIs(get_media_base_form(), BaseMediaForm)
    
    def test_get_media_form(self):
        bases = get_media_form(models.Media).__bases__
        self.assertIn(BaseMediaForm, bases)
        self.assertNotIn(AlternateMediaForm, bases)

    @override_settings(WAGTAILMEDIA_MEDIA_FORM='wagtailmedia.tests.testapp.forms.AlternateMediaForm')
    def test_overridden_base_form(self):
        self.assertIs(get_media_base_form(), AlternateMediaForm)
    
    @patch('wagtailmedia.forms.media_base_form', AlternateMediaForm)
    def test_get_overridden_media_form(self):
        bases = get_media_form(models.Media).__bases__
        self.assertNotIn(BaseMediaForm, bases)
        self.assertIn(AlternateMediaForm, bases)
