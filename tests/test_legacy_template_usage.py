import unittest

from unittest.mock import patch

from django import forms
from django.http import HttpResponse
from django.template import Context, Template
from django.test import TestCase, override_settings
from django.urls import path
from django.views import View
from wagtail import VERSION as WAGTAIL_VERSION


class DummyForm(forms.Form):
    media_file = forms.FileField(label="Change media file:", required=False)


class DummyFileFieldView(View):
    template_string = """
        {% load media_tags %}
        {% wagtail_version_gte "6.0" as wagtail_gte_60 %}  # Update version as needed
        {% if wagtail_gte_60 %}
            {% include "wagtailmedia/media/_file_field.html" %}
        {% else %}
            {% include "wagtailmedia/media/_file_field_legacy.html" %}
        {% endif %}
    """

    def get(self, request, *args, **kwargs):
        template = Template(self.template_string)
        form = DummyForm()  # Create an instance of the form
        context_data = self.get_context_data(form=form, **kwargs)
        return HttpResponse(template.render(Context(context_data)))

    def get_context_data(self, **kwargs):
        # Mock 'media' and 'field' as they are used in the templates
        return {
            "media": {
                "url": "http://example.com/media/file.mp3",
                "filename": "file.mp3",
            },
            "field": kwargs["form"]["media_file"],  # Passing the actual form field
            **kwargs,
        }


urlpatterns = [
    # Temporary URL for testing
    path(
        "test-filefield-template/",
        DummyFileFieldView.as_view(),
        name="test-filefield-template",
    ),
]


@override_settings(ROOT_URLCONF=__name__)  # Override ROOT_URLCONF during this test
class WagtailVersionFileFieldTemplateTests(TestCase):
    @patch(
        "wagtailmedia.templatetags.media_tags.get_main_version", return_value="5.2"
    )  # Version for legacy template
    def test_legacy_template_loaded(self, _mock):
        response = self.client.get("/test-filefield-template/")
        self.assertTemplateUsed(response, "wagtailmedia/media/_file_field_legacy.html")

    @unittest.skipUnless(WAGTAIL_VERSION >= (6, 0), "Requires Wagtail 6.0 or higher")
    @patch(
        "wagtailmedia.templatetags.media_tags.get_main_version", return_value="6.0"
    )  # Version for new template
    def test_new_template_loaded(self, _mock):
        response = self.client.get("/test-filefield-template/")
        self.assertTemplateUsed(response, "wagtailmedia/media/_file_field.html")
