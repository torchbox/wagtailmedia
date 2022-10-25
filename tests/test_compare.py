from unittest import skipUnless

from django.core.files.base import ContentFile
from django.test import TestCase
from django.utils.safestring import SafeString

from wagtail import VERSION as WAGTAIL_VERSION
from wagtail.core.models import Page

from tests.testapp.models import BlogStreamPage
from wagtailmedia.edit_handlers import MediaFieldComparison
from wagtailmedia.models import get_media_model
from wagtailmedia.utils import format_audio_html, format_video_html


Media = get_media_model()


class MediaFieldComparisonTest(TestCase):
    comparison_class = MediaFieldComparison

    @classmethod
    def setUpTestData(cls):
        cls.audio_a = Media.objects.create(
            title="Test audio 2",
            duration=1000,
            file=ContentFile("Test1", name="test1.mp3"),
            type="audio",
        )

        cls.audio_b = Media.objects.create(
            title="Test audio 2",
            duration=100,
            file=ContentFile("Test2", name="test2.mp3"),
            type="audio",
        )

        cls.video_a = Media.objects.create(
            title="Test video 1",
            duration=1024,
            file=ContentFile("Test1", name="test1.mp4"),
            type="video",
        )

        cls.video_b = Media.objects.create(
            title="Test video 2",
            duration=1024,
            file=ContentFile("Test1", name="test2.mp4"),
            type="video",
        )

        root_page = Page.objects.first()
        cls.test_instance = BlogStreamPage(
            title="Post",
            slug="post",
            author="Joe Bloggs",
            date="1984-01-01",
            featured_media=cls.audio_a,
        )
        root_page.add_child(instance=cls.test_instance)

    def test_hasnt_changed(self):
        comparison = self.comparison_class(
            BlogStreamPage._meta.get_field("featured_media"),
            BlogStreamPage(featured_media=self.audio_a),
            BlogStreamPage(featured_media=self.audio_a),
        )

        self.assertTrue(comparison.is_field)
        self.assertFalse(comparison.is_child_relation)
        self.assertEqual(comparison.field_label(), "Featured media")
        self.assertFalse(comparison.has_changed())

        diff = comparison.htmldiff()
        self.assertHTMLEqual(
            diff,
            f'<div class="comparison--media">{format_audio_html(self.audio_a)}</div>',
        )
        self.assertIsInstance(diff, SafeString)

        comparison = self.comparison_class(
            BlogStreamPage._meta.get_field("featured_media"),
            BlogStreamPage(featured_media=self.video_a),
            BlogStreamPage(featured_media=self.video_a),
        )
        self.assertFalse(comparison.has_changed())

        diff = comparison.htmldiff()
        self.assertHTMLEqual(
            diff,
            f'<div class="comparison--media">{format_video_html(self.video_a)}</div>',
        )

    def test_has_changed(self):
        comparison = self.comparison_class(
            BlogStreamPage._meta.get_field("featured_media"),
            BlogStreamPage(featured_media=self.audio_a),
            BlogStreamPage(featured_media=self.audio_b),
        )

        self.assertTrue(comparison.has_changed())
        diff = comparison.htmldiff()
        self.assertHTMLEqual(
            diff,
            f'<div class="comparison--media deletion">{ format_audio_html(self.audio_a) }</div>'
            f'<div class="comparison--media addition">{ format_audio_html(self.audio_b) }</div>',
        )
        self.assertIsInstance(diff, SafeString)

        comparison = self.comparison_class(
            BlogStreamPage._meta.get_field("featured_media"),
            BlogStreamPage(featured_media=self.audio_a),
            BlogStreamPage(featured_media=self.video_a),
        )
        self.assertTrue(comparison.has_changed())
        self.assertHTMLEqual(
            comparison.htmldiff(),
            f'<div class="comparison--media deletion">{format_audio_html(self.audio_a)}</div>'
            f'<div class="comparison--media addition">{format_video_html(self.video_a)}</div>',
        )

        comparison = self.comparison_class(
            BlogStreamPage._meta.get_field("featured_media"),
            BlogStreamPage(featured_media=self.video_a),
            BlogStreamPage(featured_media=self.video_b),
        )
        self.assertTrue(comparison.has_changed())
        self.assertHTMLEqual(
            comparison.htmldiff(),
            f'<div class="comparison--media deletion">{format_video_html(self.video_a)}</div>'
            f'<div class="comparison--media addition">{format_video_html(self.video_b)}</div>',
        )

    def test_empty_compare(self):
        comparison = self.comparison_class(
            BlogStreamPage._meta.get_field("featured_media"),
            BlogStreamPage(featured_media=None),
            BlogStreamPage(featured_media=None),
        )

        self.assertTrue(comparison.is_field)
        self.assertFalse(comparison.is_child_relation)
        self.assertEqual(comparison.field_label(), "Featured media")
        self.assertFalse(comparison.has_changed())

        self.assertHTMLEqual(comparison.htmldiff(), "")

    @skipUnless(
        WAGTAIL_VERSION >= (3, 0), "comparison_class_registry only added in Wagtail 3.0"
    )
    def test_our_class_in_comparison_class_registry(self):
        from wagtail.admin.compare import comparison_class_registry

        self.assertIn(Media, comparison_class_registry.values_by_fk_related_model)
        self.assertIs(
            comparison_class_registry.values_by_fk_related_model[Media],
            MediaFieldComparison,
        )
