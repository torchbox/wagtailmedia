from django.test import TestCase
from django.utils.safestring import SafeString
from testapp.models import BlogStreamPage

from wagtailmedia.blocks import (
    AudioChooserBlock,
    MediaChooserBlockComparison,
    VideoChooserBlock,
)
from wagtailmedia.edit_handlers import MediaFieldComparison
from wagtailmedia.models import get_media_model
from wagtailmedia.utils import format_audio_html, format_video_html

from .utils import create_audio, create_video


Media = get_media_model()


class MediaBlockComparisonTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.audio_a = create_audio("Test audio 1", duration=1000)
        cls.audio_b = create_audio("Test audio 2", duration=100)
        cls.video_a = create_video("Test video 1", duration=1024)
        cls.video_b = create_video("Test video 2", duration=1024)

    def tearDown(self):
        for m in [self.audio_a, self.audio_b, self.video_a, self.video_b]:
            m.delete()


class MediaFieldComparisonTest(MediaBlockComparisonTestCase):
    comparison_class = MediaFieldComparison

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

        self.assertHTMLEqual(
            comparison.htmldiff(),
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
            f'<div class="comparison--media deletion">{format_audio_html(self.audio_a)}</div>'
            f'<div class="comparison--media addition">{format_audio_html(self.audio_b)}</div>',
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

    def test_our_class_in_comparison_class_registry(self):
        from wagtail.admin.compare import comparison_class_registry

        self.assertIn(Media, comparison_class_registry.values_by_fk_related_model)
        self.assertIs(
            comparison_class_registry.values_by_fk_related_model[Media],
            MediaFieldComparison,
        )


class MediaBlockComparisonTest(MediaBlockComparisonTestCase):
    comparison_class = MediaChooserBlockComparison

    def test_comparison_hasnt_changed(self):
        comparison = self.comparison_class(
            AudioChooserBlock(), True, True, self.audio_a, self.audio_a
        )
        self.assertFalse(comparison.has_changed())
        diff = comparison.htmldiff()
        self.assertHTMLEqual(
            diff,
            f'<div class="comparison--media">{format_audio_html(self.audio_a)}</div>',
        )
        self.assertIsInstance(diff, SafeString)

        comparison = self.comparison_class(
            VideoChooserBlock(), True, True, self.video_a, self.video_a
        )
        self.assertFalse(comparison.has_changed())
        self.assertHTMLEqual(
            comparison.htmldiff(),
            f'<div class="comparison--media">{format_video_html(self.video_a)}</div>',
        )

    def test_comparison_has_changed(self):
        comparison = self.comparison_class(
            AudioChooserBlock(), True, True, self.audio_a, self.audio_b
        )
        self.assertTrue(comparison.has_changed())
        diff = comparison.htmldiff()
        self.assertHTMLEqual(
            diff,
            f'<div class="comparison--media deletion">{format_audio_html(self.audio_a)}</div>'
            f'<div class="comparison--media addition">{format_audio_html(self.audio_b)}</div>',
        )

        comparison = self.comparison_class(
            VideoChooserBlock(), True, True, self.video_a, self.video_b
        )
        self.assertTrue(comparison.has_changed())
        self.assertHTMLEqual(
            comparison.htmldiff(),
            f'<div class="comparison--media deletion">{format_video_html(self.video_a)}</div>'
            f'<div class="comparison--media addition">{format_video_html(self.video_b)}</div>',
        )
