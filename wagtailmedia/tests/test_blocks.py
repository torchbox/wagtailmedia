from django.core.files.base import ContentFile
from django.test import TestCase

from wagtailmedia.blocks import AbstractMediaChooserBlock
from wagtailmedia.models import Media


class BlockTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        fake_file = ContentFile("Test")
        fake_file.name = "test.mp3"

        cls.media = Media.objects.create(
            title="Test", duration=1000, file=fake_file, type="audio"
        )

    def test_abstract_render_raises_not_implemented_error(self):
        block = AbstractMediaChooserBlock()
        with self.assertRaises(NotImplementedError):
            block.render(self.media)

    def test_render_calls_render_basic(self):
        class TestMediaChooserBlock(AbstractMediaChooserBlock):
            def render_basic(self, value, context=None):
                return value.file.name

        block = TestMediaChooserBlock()
        self.assertEqual(block.render(self.media), "media/test.mp3")
