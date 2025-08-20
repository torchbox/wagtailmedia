from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import transaction
from django.template import Context, Template
from django.test import TestCase, override_settings

from wagtailmedia.forms import get_media_form
from wagtailmedia.models import get_media_model


Media = get_media_model()


class TestMediaValidation(TestCase):
    def test_duration_validation(self):
        # ensure duration is optional
        media = Media(
            title="Test media file",
            file=ContentFile("A boring example movie", name="movie.mp4"),
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
            media = Media(
                title="Test media file",
                file=ContentFile("A boring example movie", name="movie.mp4"),
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
            media = Media(
                title="Test media file",
                file=ContentFile("A boring example movie", name="movie.mp4"),
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
            media = Media(
                title="Test media file",
                file=ContentFile("A boring example movie", name="movie.mp4"),
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
        with self.captureOnCommitCallbacks(execute=True):
            media = Media.objects.create(title="Test media file", duration=100)

        # Search for it
        results = Media.objects.search("Test")
        self.assertEqual(list(results), [media])

    def test_operators(self):
        with self.captureOnCommitCallbacks(execute=True):
            aaa_media = Media.objects.create(title="AAA Test media", duration=100)
            zzz_media = Media.objects.create(title="ZZZ Test media", duration=100)

        results = Media.objects.search("aaa test", operator="and")
        self.assertEqual(list(results), [aaa_media])

        results = Media.objects.search("aaa test", operator="or")
        sorted_results = sorted(results, key=lambda media: media.title)
        self.assertEqual(sorted_results, [aaa_media, zzz_media])

    def test_custom_ordering(self):
        with self.captureOnCommitCallbacks(execute=True):
            aaa_media = Media.objects.create(title="AAA Test media", duration=100)
            zzz_media = Media.objects.create(title="ZZZ Test media", duration=100)

        results = Media.objects.order_by("title").search(
            "Test", order_by_relevance=False
        )
        self.assertEqual(list(results), [aaa_media, zzz_media])
        results = Media.objects.order_by("-title").search(
            "Test", order_by_relevance=False
        )
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
        media = Media(
            file=File(ContentFile("A boring example movie", name="movie.mp4"))
        )
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
        media = Media(file=File(ContentFile("A boring example movie", name="movie")))
        self.assertEqual(
            media.sources,
            [
                {
                    "src": "/media/movie",
                    "type": "application/octet-stream",
                }
            ],
        )

    def test_thumbnail_filename(self):
        media = Media(
            file=File(ContentFile("A boring example movie", name="movie.mp4")),
        )

        self.assertEqual(media.thumbnail_filename, "")
        media.thumbnail = ContentFile("Thumbnail", name="thumbnail.jpg")
        self.assertEqual(media.thumbnail_filename, "thumbnail.jpg")


class TestMediaFilenameProperties(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.media = Media(
            title="Test media",
            duration=100,
            file=ContentFile("A amazing example music video", name="example.mp4"),
        )
        cls.media.save()

        cls.extensionless_media = Media(
            title="Test media",
            duration=101,
            file=ContentFile("A boring example music video", name="example"),
        )
        cls.extensionless_media.save()

    def test_filename(self):
        self.assertRegex(self.media.filename, r"example(_\w{7})?.mp4")
        self.assertRegex(self.extensionless_media.filename, r"example(_\w{7})?")

    def test_file_extension(self):
        self.assertEqual("mp4", self.media.file_extension)
        self.assertEqual("", self.extensionless_media.file_extension)

    def tearDown(self):
        self.media.delete()
        self.extensionless_media.delete()


class TestMediaFilesDeletion(TestCase):
    def test_media_file_deleted_oncommit(self):
        with self.captureOnCommitCallbacks(execute=True):
            with transaction.atomic():
                media = Media.objects.create(
                    title="",
                    file=ContentFile(
                        "A boring example movie", name="movie-for-deletion.mp4"
                    ),
                    duration=1,
                )
                filename = media.file.name

                self.assertTrue(media.file.storage.exists(filename))

                media.delete()
                self.assertTrue(media.file.storage.exists(filename))
        self.assertFalse(media.file.storage.exists(filename))


@override_settings(WAGTAILMEDIA={"MEDIA_MODEL": "wagtailmedia_tests.CustomMedia"})
class TestMediaModel(TestCase):
    def test_media_model(self):
        cls = get_media_model()
        self.assertEqual(
            f"{cls._meta.app_label}.{cls.__name__}",
            "wagtailmedia_tests.CustomMedia",
        )


class TestMediaValidateExtensions(TestCase):
    def _create(self, file, type, thumbnail=None):
        return Media.objects.create(
            title="Test media", file=file, type=type, thumbnail=thumbnail
        )

    def test_create_with_invalid_thumbnail_extension(self):
        """Checks if created media has an expected extension"""
        self.media = self._create("test.mp3", type="audio", thumbnail="thumb.doc")

        with self.assertRaises(ValidationError):
            self.media.full_clean()

    def test_create_with_valid_thumbnail_extension(self):
        """Checks if the uploaded media has the expected thumnail extensions."""
        self.media = self._create("test.mp3", type="audio", thumbnail="thumb.png")
        try:
            self.media.full_clean()
        except ValidationError:
            self.fail("Validation error is raised even when valid file name is passed")

    def test_create_audio_with_invalid_extension(self):
        self.media = self._create("test.pdf", type="audio")
        with self.assertRaises(ValidationError):
            self.media.full_clean()

    def test_create_audio_with_valid_extension(self):
        self.media = self._create("test.mp3", type="audio")
        try:
            self.media.full_clean()
        except ValidationError:
            self.fail("Validation error is raised even when valid file name is passed")

    @override_settings(WAGTAILMEDIA={"AUDIO_EXTENSIONS": ["pdf"]})
    def test_create_audio_with_custom_extension(self):
        self.media = self._create("test.pdf", type="audio")
        try:
            self.media.full_clean()
        except ValidationError:
            self.fail("Validation error is raised even when valid file name is passed")

    def test_create_video_with_invalid_extension(self):
        self.media = self._create("test.pdf", type="video")
        with self.assertRaises(ValidationError):
            self.media.full_clean()

    def test_create_video_with_valid_extension(self):
        self.media = self._create("test.avi", type="video")
        try:
            self.media.full_clean()
        except ValidationError:
            self.fail("Validation error is raised even when valid file name is passed")

    @override_settings(WAGTAILMEDIA={"VIDEO_EXTENSIONS": []})
    def test_create_video_with_any_extension(self):
        self.media = self._create("test.pdf", type="video")
        try:
            self.media.full_clean()
        except ValidationError:
            self.fail("Validation error is raised even when valid file name is passed")

    def tearDown(self):
        self.media.delete()
