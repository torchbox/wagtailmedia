from django.core.files.base import ContentFile
from django.test import TestCase
from wagtailmedia.models import get_media_model
from wagtailmedia.utils import format_audio_html, format_video_html


Media = get_media_model()


class MediaUtilsTest(TestCase):
    def test_format_audio_html(self):
        audio = Media(
            title="Test audio 2",
            duration=1000,
            file=ContentFile("Test1", name="test1.mp3"),
            type="audio",
        )

        self.assertEqual(
            format_audio_html(audio),
            f'<audio controls>\n<source src="{audio.url}" type="audio/mpeg">\n'
            f"<p>Your browser does not support the audio element.</p>\n</audio>",
        )

    def test_format_video_html(self):
        video = Media(
            title="Test video 1",
            duration=1024,
            file=ContentFile("Test1", name="test1.mp4"),
            type="video",
        )

        self.assertEqual(
            format_video_html(video),
            f'<video controls>\n<source src="{video.url}" type="video/mp4">\n'
            f"<p>Your browser does not support the video element.</p>\n</video>",
        )
