from __future__ import unicode_literals

from django.core.files import File
from django.core.files.base import ContentFile
from django.test import TestCase

from six import b

from wagtailmedia import models
from wagtailmedia.forms import get_media_form


class TestMediaQuerySet(TestCase):
    def test_search_method(self):
        # Make a test media
        media = models.Media.objects.create(title="Test media file", duration=100)

        # Search for it
        results = models.Media.objects.search("Test")
        self.assertEqual(list(results), [media])

    def test_operators(self):
        aaa_media = models.Media.objects.create(title="AAA Test media", duration=100)
        zzz_media = models.Media.objects.create(title="ZZZ Test media", duration=100)

        results = models.Media.objects.search("aaa test", operator='and')
        self.assertEqual(list(results), [aaa_media])

        results = models.Media.objects.search("aaa test", operator='or')
        sorted_results = sorted(results, key=lambda media: media.title)
        self.assertEqual(sorted_results, [aaa_media, zzz_media])

    def test_custom_ordering(self):
        aaa_media = models.Media.objects.create(title="AAA Test media", duration=100)
        zzz_media = models.Media.objects.create(title="ZZZ Test media", duration=100)

        results = models.Media.objects.order_by('title').search("Test")
        self.assertEqual(list(results), [aaa_media, zzz_media])
        results = models.Media.objects.order_by('-title').search("Test")
        self.assertEqual(list(results), [zzz_media, aaa_media])

    def _test_form_init_with_non_editable_field(self, media_type, field_name):
        MediaForm = get_media_form(models.Media)
        models.Media._meta.get_field(field_name).editable = False
        media = models.Media.objects.create(title="Test media file", type=media_type, duration=100)
        try:
            MediaForm(media)
        finally:
            models.Media._meta.get_field(field_name).editable = True

    def test_form_init_with_non_editable_field(self):
        for media_type in ('audio', 'video'):
            for field_name in ('width', 'height', 'thumbnail'):
                self._test_form_init_with_non_editable_field(media_type, field_name)

    def test_audio_form_presents_thumbnail(self):
        MediaForm = get_media_form(models.Media)
        media = models.Media.objects.create(title="Test media file", type='audio', duration=100)
        self.assertIn('thumbnail', MediaForm(instance=media).fields.keys())


class TestAbstractMediaInterfaceModel(TestCase):
    def test_sources_mp4_type(self):
        fake_file = ContentFile(b("A boring example movie"))
        fake_file.name = 'movie.mp4'
        media = models.Media()
        media.file = File(fake_file)
        self.assertEqual(media.sources, [{
            'src': '/media/movie.mp4',
            'type': 'video/mp4',
        }])

    def test_sources_unknown_type(self):
        fake_file = ContentFile(b("A boring example movie"))
        fake_file.name = 'movie'
        media = models.Media()
        media.file = File(fake_file)
        self.assertEqual(media.sources, [{
            'src': '/media/movie',
            'type': 'application/octet-stream',
        }])
