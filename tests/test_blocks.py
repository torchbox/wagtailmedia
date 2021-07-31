from django.core.files.base import ContentFile
from django.test import TestCase
from django.urls import reverse

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

    def test_media_block_get_form_state(self):
        block = AbstractMediaChooserBlock()
        form_state = block.get_form_state(self.media.id)
        self.assertEqual(self.media.id, form_state["id"])
        self.assertEqual(self.media.title, form_state["title"])
        edit_link = reverse("wagtailmedia:edit", args=(self.media.id,))
        self.assertEqual(edit_link, form_state["edit_link"])
