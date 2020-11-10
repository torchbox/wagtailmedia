from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import transaction
from django.template import Context, Template
from django.test import TestCase, TransactionTestCase, override_settings

from wagtail.core.models import Collection

from six import b

from wagtailmedia import signal_handlers
from wagtailmedia.forms import get_media_form
from wagtailmedia.models import Media, get_media_model


class TestMediaValidation(TestCase):
    def test_duration_validation(self):
        # ensure duration is optional
        fake_file = ContentFile(b("A boring example movie"))
        fake_file.name = "movie.mp4"
        media = Media(
            title="Test media file",
            file=File(fake_file),
            type="video",
        )
        media.full_clean()

        # ensure cannot be negative
        media.duration = -100
        with self.assertRaises(ValidationError):
            media.full_clean()

        # ensure empty values are valid
        for value in (0, 0.0, None, ""):
            with self.subTest(value=value):
                media.duration = value
                media.full_clean()
                self.assertEqual(media.duration, 0)

        # ensure fractional durations are preserved
        media.duration = 100.5
        media.full_clean()
        self.assertEqual(media.duration, 100.5)


class TestMediaTemplating(TestCase):
    def test_duration_rendering(self):
        template = Template("{{ media.duration }}")
        for value, result in (
            (None, "0.0"),
            ("", "0.0"),
            (0, "0.0"),
            (0.1, "0.1"),
            (1, "1.0"),
            (1234567.7654321, "1234567.7654321"),
        ):
            fake_file = ContentFile(b("A boring example movie"))
            fake_file.name = "movie.mp4"
            media = Media(
                title="Test media file",
                file=File(fake_file),
                type="video",
            )
            media.duration = value
            media.full_clean()
            media.save()
            media.refresh_from_db()
            actual = template.render(Context({"media": media}))
            self.assertEqual(actual, result)

    def test_duration_display_as_int(self):
        template = Template('{{ media.duration|floatformat:"0" }}')
        for value, result in (
            (None, "0"),
            ("", "0"),
            (0, "0"),
            (0.1, "0"),
            (1, "1"),
            (1234567.7654321, "1234568"),
        ):
            fake_file = ContentFile(b("A boring example movie"))
            fake_file.name = "movie.mp4"
            media = Media(
                title="Test media file",
                file=File(fake_file),
                type="video",
            )
            media.duration = value
            media.full_clean()
            media.save()
            media.refresh_from_db()
            actual = template.render(Context({"media": media}))
            self.assertEqual(actual, result)

    def test_duration_display_as_tenths(self):
        template = Template("{{ media.duration|floatformat }}")
        for value, result in (
            (None, "0"),
            ("", "0"),
            (0, "0"),
            (0.1, "0.1"),
            (1, "1"),
            (1234567.7654321, "1234567.8"),
        ):
            fake_file = ContentFile(b("A boring example movie"))
            fake_file.name = "movie.mp4"
            media = Media(
                title="Test media file",
                file=File(fake_file),
                type="video",
            )
            media.duration = value
            media.full_clean()
            media.save()
            media.refresh_from_db()
            actual = template.render(Context({"media": media}))
            self.assertEqual(actual, result)


class TestMediaQuerySet(TestCase):
    def test_search_method(self):
        # Make a test media
        media = Media.objects.create(title="Test media file", duration=100)

        # Search for it
        results = Media.objects.search("Test")
        self.assertEqual(list(results), [media])

    def test_operators(self):
        aaa_media = Media.objects.create(title="AAA Test media", duration=100)
        zzz_media = Media.objects.create(title="ZZZ Test media", duration=100)

        results = Media.objects.search("aaa test", operator="and")
        self.assertEqual(list(results), [aaa_media])

        results = Media.objects.search("aaa test", operator="or")
        sorted_results = sorted(results, key=lambda media: media.title)
        self.assertEqual(sorted_results, [aaa_media, zzz_media])

    def test_custom_ordering(self):
        aaa_media = Media.objects.create(title="AAA Test media", duration=100)
        zzz_media = Media.objects.create(title="ZZZ Test media", duration=100)

        results = Media.objects.order_by("title").search("Test")
        self.assertEqual(list(results), [aaa_media, zzz_media])
        results = Media.objects.order_by("-title").search("Test")
        self.assertEqual(list(results), [zzz_media, aaa_media])

    def _test_form_init_with_non_editable_field(self, media_type, field_name):
        MediaForm = get_media_form(Media)
        Media._meta.get_field(field_name).editable = False
        media = Media.objects.create(
            title="Test media file", type=media_type, duration=100
        )
        try:
            MediaForm(media)
        finally:
            Media._meta.get_field(field_name).editable = True

    def test_form_init_with_non_editable_field(self):
        for media_type in ("audio", "video"):
            for field_name in ("width", "height", "thumbnail"):
                self._test_form_init_with_non_editable_field(media_type, field_name)

    def test_audio_form_presents_thumbnail(self):
        MediaForm = get_media_form(Media)
        media = Media.objects.create(
            title="Test media file", type="audio", duration=100
        )
        self.assertIn("thumbnail", MediaForm(instance=media).fields.keys())


class TestAbstractMediaInterfaceModel(TestCase):
    def test_sources_mp4_type(self):
        fake_file = ContentFile(b("A boring example movie"))
        fake_file.name = "movie.mp4"
        media = Media()
        media.file = File(fake_file)
        self.assertEqual(
            media.sources,
            [
                {
                    "src": "/media/movie.mp4",
                    "type": "video/mp4",
                }
            ],
        )

    def test_sources_unknown_type(self):
        fake_file = ContentFile(b("A boring example movie"))
        fake_file.name = "movie"
        media = Media()
        media.file = File(fake_file)
        self.assertEqual(
            media.sources,
            [
                {
                    "src": "/media/movie",
                    "type": "application/octet-stream",
                }
            ],
        )


class TestMediaFilenameProperties(TransactionTestCase):
    def setUp(self):
        # Required to create root collection because the TransactionTestCase
        # does not make initial data loaded in migrations available and
        # serialized_rollback=True causes other problems in the test suite.
        # ref: https://docs.djangoproject.com/en/3.0/topics/testing/overview/#rollback-emulation
        Collection.objects.get_or_create(
            name="Root",
            path="0001",
            depth=1,
            numchild=0,
        )

        self.media = Media(title="Test media", duration=100)
        self.media.file.save(
            "example.mp4", ContentFile("A amazing example music video")
        )

        self.extensionless_media = Media(title="Test media", duration=101)
        self.extensionless_media.file.save(
            "example", ContentFile("A boring example music video")
        )

    def test_filename(self):
        self.assertEqual("example.mp4", self.media.filename)
        self.assertEqual("example", self.extensionless_media.filename)

    def test_file_extension(self):
        self.assertEqual("mp4", self.media.file_extension)
        self.assertEqual("", self.extensionless_media.file_extension)

    def tearDown(self):
        self.media.delete()
        self.extensionless_media.delete()


class TestMediaFilesDeletion(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # ensure the signal handlers are registred
        signal_handlers.register_signal_handlers()

    def setUp(self):
        # Required to create root collection because the TransactionTestCase
        # does not make initial data loaded in migrations available and
        # serialized_rollback=True causes other problems in the test suite.
        # ref: https://docs.djangoproject.com/en/3.0/topics/testing/overview/#rollback-emulation
        Collection.objects.get_or_create(
            name="Root",
            path="0001",
            depth=1,
            numchild=0,
        )

    def test_media_file_deleted_oncommit(self):
        with transaction.atomic():
            fake_file = ContentFile(b("A boring example movie"))
            fake_file.name = "movie-for-deletion.mp4"

            media = get_media_model().objects.create(
                title="", file=File(fake_file), duration=1
            )
            filename = media.file.name

            self.assertTrue(media.file.storage.exists(filename))
            media.delete()
            self.assertTrue(media.file.storage.exists(filename))
        self.assertFalse(media.file.storage.exists(filename))


@override_settings(WAGTAILMEDIA_MEDIA_MODEL="wagtailmedia_tests.CustomMedia")
class TestMediaFilesDeletionForCustomModels(TestMediaFilesDeletion):
    def test_media_model(self):
        cls = get_media_model()
        self.assertEqual(
            "%s.%s" % (cls._meta.app_label, cls.__name__),
            "wagtailmedia_tests.CustomMedia",
        )
