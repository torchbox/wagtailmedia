from django.core.files.base import ContentFile
from django.test import TestCase
from django.urls import reverse

from wagtailmedia.blocks import (
    AbstractMediaChooserBlock,
    AudioChooserBlock,
    MediaChooserBlockComparison,
    VideoChooserBlock,
)
from wagtailmedia.models import Media


class BlockTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.audio = Media.objects.create(
            title="Test audio",
            duration=1000,
            file=ContentFile("Test", name="test.mp3"),
            type="audio",
        )

        cls.video = Media.objects.create(
            title="Test video",
            duration=1024,
            file=ContentFile("Test", name="test.mp4"),
            type="video",
        )

    def test_abstract_render_raises_not_implemented_error(self):
        block = AbstractMediaChooserBlock()
        with self.assertRaises(NotImplementedError):
            block.render(self.audio)

    def test_render_calls_render_basic(self):
        class TestMediaChooserBlock(AbstractMediaChooserBlock):
            def render_basic(self, value, context=None):
                return value.file.name

        block = TestMediaChooserBlock()
        self.assertRegex(block.render(self.audio), r"media/test(_\w{7})?.mp3")

    def test_media_block_get_form_state(self):
        block = AbstractMediaChooserBlock()
        form_state = block.get_form_state(self.audio.id)
        self.assertEqual(self.audio.id, form_state["id"])
        self.assertEqual(self.audio.title, form_state["title"])
        edit_link = reverse("wagtailmedia:edit", args=(self.audio.id,))
        self.assertEqual(edit_link, form_state["edit_url"])

    def test_abstract_media_block_queryset(self):
        block = AbstractMediaChooserBlock()

        self.assertQuerySetEqual(
            block.field.queryset.order_by("pk"),
            Media.objects.order_by("pk"),
        )

        block = AbstractMediaChooserBlock(media_type="audio")
        self.assertQuerySetEqual(
            block.field.queryset.order_by("pk"),
            Media.objects.filter(type="audio").order_by("pk"),
        )

        block = AbstractMediaChooserBlock(media_type="subspace-transmission")
        self.assertQuerySetEqual(block.field.queryset, Media.objects.none())

    def test_audio_chooser_block_type(self):
        block = AudioChooserBlock()
        self.assertEqual(block.media_type, "audio")

    def test_audio_chooser_block_field_queryset(self):
        block = AudioChooserBlock()
        self.assertListEqual(
            list(block.field.queryset.values_list("pk", flat=True)),
            list(Media.objects.filter(type="audio").values_list("pk", flat=True)),
        )

    def test_audio_chooser_block_rendering(self):
        block = AudioChooserBlock()
        self.assertEqual(
            block.render(self.audio),
            f'<audio controls>\n<source src="{self.audio.file.url}" type="audio/mpeg">\n'
            f"<p>Your browser does not support the audio element.</p>\n</audio>",
        )

        # will return an empty value if trying to render with the wrong media type
        self.assertEqual(block.render(self.video), "")

    def test_video_chooser_block_type(self):
        block = VideoChooserBlock()
        self.assertEqual(block.media_type, "video")

    def test_video_chooser_block_field_queryset(self):
        block = VideoChooserBlock()
        self.assertListEqual(
            list(block.field.queryset.values_list("pk", flat=True)),
            list(Media.objects.filter(type="video").values_list("pk", flat=True)),
        )

    def test_video_chooser_block_rendering(self):
        block = VideoChooserBlock()
        self.assertEqual(
            block.render(self.video),
            f'<video controls>\n<source src="{self.video.file.url}" type="video/mp4">\n'
            f"<p>Your browser does not support the video element.</p>\n</video>",
        )

        # will return an empty value if trying to render with the wrong media type
        self.assertEqual(block.render(self.audio), "")

    def test_comparison_class(self):
        self.assertIs(
            AbstractMediaChooserBlock().get_comparison_class(),
            MediaChooserBlockComparison,
        )
        self.assertIs(
            AudioChooserBlock().get_comparison_class(), MediaChooserBlockComparison
        )
        self.assertIs(
            VideoChooserBlock().get_comparison_class(), MediaChooserBlockComparison
        )
