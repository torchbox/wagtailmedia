from __future__ import unicode_literals

from django.test import TestCase

from wagtailmedia import models


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
