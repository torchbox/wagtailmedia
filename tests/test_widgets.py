from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from wagtailmedia import widgets
from wagtailmedia.widgets import AdminAudioChooser, AdminMediaChooser, AdminVideoChooser


class WidgetTests(TestCase):
    def test_get_value_data(self):
        class StubModelManager:
            def get(self, pk):
                return StubMediaModel(pk)

        class StubMediaModel:
            objects = StubModelManager()

            def __init__(self, pk):
                self.pk = pk
                self.id = pk
                self.title = "foo"

        test_data = [
            # (input value, expected output value)
            (None, None),
            (3, {"id": 3, "title": "foo", "edit_link": "/edit/3/"}),
            (StubMediaModel(3), {"id": 3, "title": "foo", "edit_link": "/edit/3/"}),
        ]

        media_chooser = widgets.AdminMediaChooser()
        media_chooser.media_model = StubMediaModel
        for input_value, expected_output in test_data:
            with patch("wagtailmedia.widgets.reverse", return_value="/edit/3/"):
                actual = media_chooser.get_value_data(input_value)
                self.assertEqual(expected_output, actual)


class AdminMediaChooserTest(TestCase):
    def test_default_chooser_text(self):
        chooser = AdminMediaChooser()
        self.assertEqual(chooser.choose_one_text, "Choose a media item")
        self.assertEqual(chooser.choose_another_text, "Choose another media item")
        self.assertEqual(chooser.link_to_chosen_text, "Edit this media item")

    def text_audio_chooser_text(self):
        chooser = AdminAudioChooser(media_type="audio")
        self.assertEqual(chooser.choose_one_text, "Choose audio")
        self.assertEqual(chooser.choose_another_text, "Choose another audio item")
        self.assertEqual(chooser.link_to_chosen_text, "Edit this audio item")

    def text_video_chooser_text(self):
        chooser = AdminVideoChooser(media_type="video")
        self.assertEqual(chooser.choose_one_text, "Choose video")
        self.assertEqual(chooser.choose_another_text, "Choose another video")
        self.assertEqual(chooser.link_to_chosen_text, "Edit this video")

    @patch("wagtailmedia.widgets.render_to_string")
    def test_render_html_uses_the_generic_chooser_url_by_default(
        self, mock_render_to_string
    ):
        chooser = AdminMediaChooser()
        chooser.render_html("test", None, {})

        render_context = mock_render_to_string.call_args[0][1]
        self.assertEqual(render_context["chooser_url"], reverse("wagtailmedia:chooser"))

    @patch("wagtailmedia.widgets.render_to_string")
    def test_render_html_uses_the_typed_chooser_url_when_using_media_type(
        self, mock_render_to_string
    ):
        chooser = AdminAudioChooser()
        chooser.render_html("test", None, {})

        render_context = mock_render_to_string.call_args[0][1]
        self.assertEqual(
            render_context["chooser_url"],
            reverse("wagtailmedia:chooser_typed", args=("audio",)),
        )
