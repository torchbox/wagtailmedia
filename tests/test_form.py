from django.test import TestCase, override_settings

from wagtailmedia.forms import format_extensions_for_accept_value, get_media_form
from wagtailmedia.models import MediaType, get_media_model
from wagtailmedia.settings import wagtailmedia_settings


class TestForm(TestCase):
    def test_file_input_accept_attribute(self):
        """Tests that the file input widget only accepts the default file extensions per media type."""
        Media = get_media_model()
        MediaForm = get_media_form(Media)
        media_type_to_extensions = {
            MediaType.VIDEO: wagtailmedia_settings.VIDEO_EXTENSIONS,
            MediaType.AUDIO: wagtailmedia_settings.AUDIO_EXTENSIONS,
        }
        for media_type, extensions in media_type_to_extensions.items():
            media = Media(type=media_type)
            form = MediaForm(instance=media)

            self.assertIn(
                f'accept="{format_extensions_for_accept_value(extensions)}"',
                form["file"].as_widget(),
            )

    @override_settings(WAGTAILMEDIA={"VIDEO_EXTENSIONS": [], "AUDIO_EXTENSIONS": []})
    def test_file_input_accept_attribute_all_extensions_allowed(self):
        """Tests that if `VIDEO_EXTENSIONS` and `AUDIO_EXTENSIONS` are set to empty lists, that the accept attribute
        allows all file extensions for the given media type.
        """
        Media = get_media_model()
        MediaForm = get_media_form(Media)
        media_type_to_extensions = {
            MediaType.VIDEO: "video/*",
            MediaType.AUDIO: "audio/*",
        }
        for media_type, accept_value in media_type_to_extensions.items():
            media = Media(type=media_type)
            form = MediaForm(instance=media)

            self.assertIn(
                f'accept="{accept_value}"',
                form["file"].as_widget(),
            )
