import json
import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.files.base import ContentFile
from django.forms.utils import ErrorDict
from django.test import TestCase, modify_settings
from django.test.utils import override_settings
from django.urls import NoReverseMatch, reverse
from testapp.models import EventPage, EventPageRelatedMedia
from wagtail.models import Collection, GroupCollectionPermission
from wagtail.test.utils import WagtailTestUtils

from wagtailmedia import models


class TestMediaIndexView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def test_simple(self):
        response = self.client.get(reverse("wagtailmedia:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/index.html")
        self.assertContains(response, "Add audio")
        self.assertContains(response, "Add video")

    @modify_settings(INSTALLED_APPS={"prepend": "tests.testextends"})
    def test_extends(self):
        response = self.client.get(reverse("wagtailmedia:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/index.html")
        self.assertNotContains(response, "Add audio")
        self.assertNotContains(response, "Add video")
        self.assertContains(response, "You shan't act")

    def test_search(self):
        response = self.client.get(reverse("wagtailmedia:index"), {"q": "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["query_string"], "Hello")

    @staticmethod
    def make_media():
        fake_file = ContentFile("A boring example song", name="song.mp3")

        for i in range(50):
            media = models.Media(
                title="Test " + str(i), duration=100 + i, file=fake_file, type="audio"
            )
            media.save()

    def test_pagination(self):
        self.make_media()

        response = self.client.get(reverse("wagtailmedia:index"), {"p": 2})

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/index.html")

        # Check that we got the correct page
        self.assertEqual(response.context["media_files"].number, 2)

    def test_pagination_invalid(self):
        self.make_media()

        response = self.client.get(reverse("wagtailmedia:index"), {"p": "Hello World!"})

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/index.html")

        # Check that we got page one
        self.assertEqual(response.context["media_files"].number, 1)

    def test_pagination_out_of_range(self):
        self.make_media()

        response = self.client.get(reverse("wagtailmedia:index"), {"p": 99999})

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/index.html")

        # Check that we got the last page
        self.assertEqual(
            response.context["media_files"].number,
            response.context["media_files"].paginator.num_pages,
        )

    def test_ordering(self):
        orderings = ["title", "-created_at"]
        for ordering in orderings:
            response = self.client.get(
                reverse("wagtailmedia:index"), {"ordering": ordering}
            )
            self.assertEqual(response.status_code, 200)


class TestMediaAddView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

        self.collection_label_tag = '<label class="w-field__label" for="id_collection" id="id_collection-label">'

    def test_action_block(self):
        with self.settings(
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [os.path.join(os.path.dirname(__file__), "templates")],
                    "APP_DIRS": True,
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.debug",
                            "django.template.context_processors.request",
                            "django.contrib.auth.context_processors.auth",
                            "django.contrib.messages.context_processors.messages",
                            "django.template.context_processors.request",
                            "wagtail.contrib.settings.context_processors.settings",
                        ],
                        "debug": True,
                    },
                }
            ]
        ):
            response = self.client.get(reverse("wagtailmedia:add", args=("audio",)))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "wagtailmedia/media/add.html")
            self.assertContains(
                response,
                '<form action="/somewhere/else" method="POST" enctype="multipart/form-data" novalidate>',
            )

    def test_get_audio(self):
        response = self.client.get(reverse("wagtailmedia:add", args=("audio",)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/add.html")

        # as standard, only the root collection exists and so no 'Collection' option
        # is displayed on the form
        self.assertNotContains(response, self.collection_label_tag)
        self.assertContains(response, "Add audio")
        self.assertNotContains(response, "Add audio or video")
        self.assertContains(
            response,
            '<form action="{}" method="POST" enctype="multipart/form-data" novalidate>'.format(
                reverse("wagtailmedia:add", args=("audio",))
            ),
            count=1,
        )

    def test_get_video(self):
        response = self.client.get(reverse("wagtailmedia:add", args=("video",)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/add.html")
        self.assertContains(response, "Add video")
        self.assertNotContains(response, "Add audio or video")
        self.assertContains(
            response,
            '<form action="{}" method="POST" enctype="multipart/form-data" novalidate>'.format(
                reverse("wagtailmedia:add", args=("video",))
            ),
            count=1,
        )

        # as standard, only the root collection exists and so no 'Collection' option
        # is displayed on the form
        self.assertNotContains(response, self.collection_label_tag)

        # draftail should NOT be a standard JS include on this page
        self.assertNotContains(response, "wagtailadmin/js/draftail.js")

    def test_get_audio_or_video(self):
        response = self.client.get(reverse("wagtailmedia:add", args=("media",)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/add.html")

        self.assertNotContains(response, "Add video")
        self.assertContains(response, "Add audio or video")

    def test_get_audio_with_collections(self):
        root_collection = Collection.get_first_root_node()
        root_collection.add_child(name="Evil plans")

        response = self.client.get(reverse("wagtailmedia:add", args=("audio",)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/add.html")

        self.assertContains(response, self.collection_label_tag)
        self.assertContains(response, "Evil plans")
        self.assertContains(response, "Add audio")
        self.assertContains(
            response,
            '<form action="{}" method="POST" enctype="multipart/form-data" novalidate>'.format(
                reverse("wagtailmedia:add", args=("audio",))
            ),
            count=1,
        )

    def test_get_video_with_collections(self):
        root_collection = Collection.get_first_root_node()
        root_collection.add_child(name="Evil plans")

        response = self.client.get(reverse("wagtailmedia:add", args=("video",)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/add.html")

        self.assertContains(response, self.collection_label_tag)
        self.assertContains(response, "Evil plans")
        self.assertContains(response, "Add video")
        self.assertContains(
            response,
            '<form action="{}" method="POST" enctype="multipart/form-data" novalidate>'.format(
                reverse("wagtailmedia:add", args=("video",))
            ),
            count=1,
        )

    def test_post_audio(self):
        # Build a fake file
        fake_file = ContentFile("A boring example song", name="song.mp3")

        # Submit
        post_data = {"title": "Test media", "file": fake_file, "duration": 100}
        response = self.client.post(
            reverse("wagtailmedia:add", args=("audio",)), post_data
        )

        # User should be redirected back to the index
        self.assertRedirects(response, reverse("wagtailmedia:index"))

        # Media should be created, and be placed in the root collection
        self.assertTrue(models.Media.objects.filter(title="Test media").exists())
        root_collection = Collection.get_first_root_node()

        media = models.Media.objects.get(title="Test media")
        self.assertEqual(media.collection, root_collection)
        self.assertEqual(media.type, "audio")

    def test_post_video(self):
        # Build a fake file
        fake_file = ContentFile("A boring example movie", name="movie.mp4")

        # Submit
        post_data = {
            "title": "Test media",
            "file": fake_file,
            "duration": 100,
            "width": 720,
            "height": 480,
        }
        response = self.client.post(
            reverse("wagtailmedia:add", args=("video",)), post_data
        )

        # User should be redirected back to the index
        self.assertRedirects(response, reverse("wagtailmedia:index"))

        # Media should be created, and be placed in the root collection
        self.assertTrue(models.Media.objects.filter(title="Test media").exists())
        root_collection = Collection.get_first_root_node()
        media = models.Media.objects.get(title="Test media")
        self.assertEqual(media.collection, root_collection)
        self.assertEqual(media.type, "video")

    def test_post_audio_with_collections(self):
        root_collection = Collection.get_first_root_node()
        evil_plans_collection = root_collection.add_child(name="Evil plans")

        # Build a fake file
        fake_file = ContentFile("A boring example song", name="song.mp3")

        # Submit
        post_data = {
            "title": "Test media",
            "file": fake_file,
            "duration": 100,
            "collection": evil_plans_collection.id,
        }
        response = self.client.post(
            reverse("wagtailmedia:add", args=("audio",)), post_data
        )

        # User should be redirected back to the index
        self.assertRedirects(response, reverse("wagtailmedia:index"))

        # Media should be created, and be placed in the Evil Plans collection
        self.assertTrue(models.Media.objects.filter(title="Test media").exists())

        media = models.Media.objects.get(title="Test media")
        self.assertEqual(media.collection, evil_plans_collection)
        self.assertEqual(media.type, "audio")

    def test_post_video_with_collections(self):
        root_collection = Collection.get_first_root_node()
        evil_plans_collection = root_collection.add_child(name="Evil plans")

        # Submit
        post_data = {
            "title": "Test media",
            "file": ContentFile("A boring example movie", name="movie.mp4"),
            "duration": 100,
            "collection": evil_plans_collection.id,
        }
        response = self.client.post(
            reverse("wagtailmedia:add", args=("video",)), post_data
        )

        # User should be redirected back to the index
        self.assertRedirects(response, reverse("wagtailmedia:index"))

        # Media should be created, and be placed in the Evil Plans collection
        self.assertTrue(models.Media.objects.filter(title="Test media").exists())

        media = models.Media.objects.get(title="Test media")
        self.assertEqual(media.collection, evil_plans_collection)
        self.assertEqual(media.type, "video")

    @override_settings(WAGTAILMEDIA={"MEDIA_MODEL": "wagtailmedia_tests.CustomMedia"})
    def test_get_with_custom_model(self):
        # both audio and video use the same template
        response = self.client.get(reverse("wagtailmedia:add", args=("video",)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/add.html")

        # Ensure the form supports file uploads
        self.assertContains(response, 'enctype="multipart/form-data"')

        # form media should be imported
        self.assertContains(response, "wagtailadmin/js/draftail.js")


class TestMediaAddViewWithLimitedCollectionPermissions(TestCase, WagtailTestUtils):
    def setUp(self):
        add_media_permission = Permission.objects.get(
            content_type__app_label="wagtailmedia", codename="add_media"
        )
        admin_permission = Permission.objects.get(
            content_type__app_label="wagtailadmin", codename="access_admin"
        )

        root_collection = Collection.get_first_root_node()
        self.evil_plans_collection = root_collection.add_child(name="Evil plans")

        conspirators_group = Group.objects.create(name="Evil conspirators")
        conspirators_group.permissions.add(admin_permission)
        GroupCollectionPermission.objects.create(
            group=conspirators_group,
            collection=self.evil_plans_collection,
            permission=add_media_permission,
        )

        user = get_user_model().objects.create_user(
            username="moriarty", email="moriarty@example.com", password="password"
        )
        user.groups.add(conspirators_group)

        self.client.login(username="moriarty", password="password")

        self.collection_label_tag = '<label class="w-field__label" for="id_collection" id="id_collection-label">'

    def test_get_audio(self):
        response = self.client.get(reverse("wagtailmedia:add", args=("audio",)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/add.html")

        # user only has access to one collection, so no 'Collection' option
        # is displayed on the form
        self.assertNotContains(response, self.collection_label_tag)
        self.assertContains(response, "Add audio")
        self.assertContains(
            response,
            '<form action="{}" method="POST" enctype="multipart/form-data" novalidate>'.format(
                reverse("wagtailmedia:add", args=("audio",))
            ),
            count=1,
        )

    def test_get_video(self):
        response = self.client.get(reverse("wagtailmedia:add", args=("video",)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/add.html")

        # user only has access to one collection, so no 'Collection' option
        # is displayed on the form
        self.assertNotContains(response, self.collection_label_tag)
        self.assertContains(response, "Add video")
        self.assertContains(
            response,
            '<form action="{}" method="POST" enctype="multipart/form-data" novalidate>'.format(
                reverse("wagtailmedia:add", args=("video",))
            ),
            count=1,
        )

    def test_post_audio(self):
        # Build a fake file
        fake_file = ContentFile("A boring example song", name="song.mp3")

        # Submit
        post_data = {"title": "Test media", "file": fake_file, "duration": 100}
        response = self.client.post(
            reverse("wagtailmedia:add", args=("audio",)), post_data
        )

        # User should be redirected back to the index
        self.assertRedirects(response, reverse("wagtailmedia:index"))

        # Media should be created with type 'audio' and in the 'evil plans' collection,
        # despite there being no collection field in the form, because that's the
        # only one the user has access to
        self.assertTrue(models.Media.objects.filter(title="Test media").exists())
        media = models.Media.objects.get(title="Test media")
        self.assertEqual(media.collection, self.evil_plans_collection)
        self.assertEqual(media.type, "audio")

    def test_post_video(self):
        # Build a fake file
        fake_file = ContentFile("A boring example movie", name="movie.mp4")

        # Submit
        post_data = {"title": "Test media", "file": fake_file, "duration": 100}
        response = self.client.post(
            reverse("wagtailmedia:add", args=("video",)), post_data
        )

        # User should be redirected back to the index
        self.assertRedirects(response, reverse("wagtailmedia:index"))

        # Media should be created with type 'video' and in the 'evil plans' collection,
        # despite there being no collection field in the form, because that's the
        # only one the user has access to
        self.assertTrue(models.Media.objects.filter(title="Test media").exists())
        media = models.Media.objects.get(title="Test media")
        self.assertEqual(media.collection, self.evil_plans_collection)
        self.assertEqual(media.type, "video")


class TestMediaEditView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

        # Build a fake file
        fake_file = ContentFile("A boring example song", name="song.mp3")

        # Create a media to edit
        self.media = models.get_media_model().objects.create(
            title="Test media", file=fake_file, duration=100
        )

    def test_simple(self):
        response = self.client.get(reverse("wagtailmedia:edit", args=(self.media.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/edit.html")
        self.assertContains(response, "Filesize")
        self.assertNotContains(response, "wagtailadmin/js/draftail.js")

    @modify_settings(INSTALLED_APPS={"prepend": "tests.testextends"})
    def test_extends(self):
        response = self.client.get(reverse("wagtailmedia:edit", args=(self.media.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/edit.html")
        self.assertNotContains(response, "Filesize")
        self.assertContains(response, "sweet-style")
        self.assertContains(response, "sweet-code")
        self.assertContains(response, "sweet-form-row")
        self.assertContains(response, "sweet-stats")

    def test_action_block(self):
        with self.settings(
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [os.path.join(os.path.dirname(__file__), "templates")],
                    "APP_DIRS": True,
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.debug",
                            "django.template.context_processors.request",
                            "django.contrib.auth.context_processors.auth",
                            "django.contrib.messages.context_processors.messages",
                            "django.template.context_processors.request",
                            "wagtail.contrib.settings.context_processors.settings",
                        ],
                        "debug": True,
                    },
                }
            ]
        ):
            response = self.client.get(
                reverse("wagtailmedia:edit", args=(self.media.id,))
            )
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "wagtailmedia/media/edit.html")
            self.assertContains(
                response,
                '<form action="/somewhere/else/edit" method="POST" enctype="multipart/form-data" novalidate>',
            )

    def test_post(self):
        # Build a fake file
        fake_file = ContentFile("A boring example song", name="song.mp3")

        # Submit title change
        post_data = {"title": "Test media changed!", "file": fake_file, "duration": 100}
        response = self.client.post(
            reverse("wagtailmedia:edit", args=(self.media.id,)), post_data
        )

        # User should be redirected back to the index
        self.assertRedirects(response, reverse("wagtailmedia:index"))

        # Media title should be changed
        self.assertEqual(
            models.Media.objects.get(id=self.media.id).title, "Test media changed!"
        )

    def test_with_missing_source_file(self):
        # Build a fake file
        fake_file = ContentFile("An ephemeral media", name="to-be-deleted.mp3")

        # Create a new media to delete the source for
        media = models.Media.objects.create(
            title="Test missing source media", file=fake_file, duration=100
        )
        media.file.delete(False)

        response = self.client.get(reverse("wagtailmedia:edit", args=(media.id,)), {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/edit.html")

        self.assertContains(response, "File not found")

    @override_settings(WAGTAILMEDIA={"MEDIA_MODEL": "wagtailmedia_tests.CustomMedia"})
    def test_get_with_custom_model(self):
        # Build a fake file
        fake_file = ContentFile("A boring example song", name="song.mp3")

        # Create a media to edit
        media = models.get_media_model().objects.create(
            title="Test custom media", file=fake_file, duration=100
        )
        response = self.client.get(reverse("wagtailmedia:edit", args=(media.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/edit.html")

        # Ensure the form supports file uploads
        self.assertContains(response, 'enctype="multipart/form-data"')

        # form media should be imported
        self.assertContains(response, "wagtailadmin/js/draftail.js")


class TestMediaDeleteView(TestCase, WagtailTestUtils):
    @classmethod
    def setUpTestData(cls):
        # Create a media to delete
        cls.media = models.Media.objects.create(title="Test media", duration=100)
        cls.delete_media_url = reverse("wagtailmedia:delete", args=(cls.media.id,))

    def setUp(self):
        self.login()

    def test_simple(self):
        response = self.client.get(self.delete_media_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/confirm_delete.html")

    def test_delete(self):
        response = self.client.post(self.delete_media_url)

        # User should be redirected back to the index
        self.assertRedirects(response, reverse("wagtailmedia:index"))

        # Media should be deleted
        self.assertFalse(models.Media.objects.filter(id=self.media.id).exists())

    # TODO: Remove once support for Wagtail < 4.1 is dropped
    @override_settings(WAGTAIL_USAGE_COUNT_ENABLED=True)
    def test_usage_link(self):
        response = self.client.get(self.delete_media_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/confirm_delete.html")
        self.assertIn("Used 0 times", str(response.content))

    def test_post_delete_file_cleanup_without_thumbnail(self):
        self.media.file = ContentFile("File", name="file.mp3")
        self.media.save()
        file_path = self.media.file.path
        storage = self.media.file.storage
        self.assertTrue(storage.exists(file_path))

        with self.captureOnCommitCallbacks(execute=True):
            self.client.post(self.delete_media_url)

        # Media should be deleted
        self.assertFalse(models.Media.objects.filter(id=self.media.id).exists())

        # The file should be deleted as well
        self.assertFalse(storage.exists(file_path))

    def test_post_delete_file_cleanup_with_thumbnail(self):
        self.media.file = ContentFile("File", name="file.mp3")
        self.media.thumbnail = ContentFile("Thumbnail", name="thumbnail.jpg")
        self.media.save()
        file_path = self.media.file.path
        thumbnail_path = self.media.thumbnail.path
        storage = self.media.file.storage

        for path in (file_path, thumbnail_path):
            self.assertTrue(storage.exists(path))

        with self.captureOnCommitCallbacks(execute=True):
            self.client.post(self.delete_media_url)

        # Media should be deleted
        self.assertFalse(models.Media.objects.filter(id=self.media.id).exists())

        # The files should be deleted as well
        for path in (file_path, thumbnail_path):
            self.assertFalse(storage.exists(path))


class TestMediaChooserView(TestCase, WagtailTestUtils):
    @classmethod
    def setUpTestData(cls):
        cls.chooser_url = reverse("wagtailmedia:chooser")

    def setUp(self):
        self.user = self.login()

    def test_simple(self):
        response = self.client.get(self.chooser_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        json_data = json.loads(response.content.decode("utf-8"))
        self.assertSetEqual(
            set(json_data.keys()),
            {"html", "step", "error_label", "error_message", "tag_autocomplete_url"},
        )
        self.assertTemplateUsed(response, "wagtailmedia/chooser/chooser.html")
        self.assertEqual(json_data["step"], "chooser")
        self.assertEqual(
            json_data["tag_autocomplete_url"], reverse("wagtailadmin_tag_autocomplete")
        )

        # draftail should NOT be a standard JS include on this page
        self.assertNotIn("wagtailadmin/js/draftail.js", json_data["html"])

    def test_search(self):
        response = self.client.get(self.chooser_url, {"q": "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["query_string"], "Hello")

    @staticmethod
    def make_media():
        fake_file = ContentFile("A boring example song", name="song.mp3")

        for i in range(50):
            media = models.Media(
                title="Test " + str(i), duration=100 + i, file=fake_file, type="audio"
            )
            media.save()

    def test_pagination(self):
        self.make_media()

        response = self.client.get(self.chooser_url, {"p": 2})

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/chooser/results.html")

        # Check that we got the correct page
        self.assertEqual(response.context["media_files"].number, 2)

    def test_pagination_invalid(self):
        self.make_media()

        response = self.client.get(self.chooser_url, {"p": "Hello World!"})

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/chooser/results.html")

        # Check that we got page one
        self.assertEqual(response.context["media_files"].number, 1)

    def test_pagination_out_of_range(self):
        self.make_media()

        response = self.client.get(self.chooser_url, {"p": 99999})

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/chooser/results.html")

        # Check that we got the last page
        self.assertEqual(
            response.context["media_files"].number,
            response.context["media_files"].paginator.num_pages,
        )

    def test_construct_queryset_hook_browse(self):
        media = models.Media.objects.create(
            title="Test media shown",
            duration=100,
            type="audio",
            uploaded_by_user=self.user,
        )
        models.Media.objects.create(
            title="Test media not shown", duration=100, type="audio"
        )

        def filter_media(media, request):
            return media.filter(uploaded_by_user=self.user)

        with self.register_hook("construct_media_chooser_queryset", filter_media):
            response = self.client.get(self.chooser_url)
        self.assertEqual(len(response.context["media_files"]), 1)
        self.assertEqual(response.context["media_files"][0], media)

    def test_construct_queryset_hook_search(self):
        with self.captureOnCommitCallbacks(execute=True):
            media = models.Media.objects.create(
                title="Test media shown",
                duration=100,
                type="audio",
                uploaded_by_user=self.user,
            )
            models.Media.objects.create(
                title="Test media not shown", duration=100, type="audio"
            )

        def filter_media(media, request):
            return media.filter(uploaded_by_user=self.user)

        with self.register_hook("construct_media_chooser_queryset", filter_media):
            response = self.client.get(self.chooser_url, {"q": "Test"})
        self.assertEqual(len(response.context["media_files"]), 1)
        self.assertEqual(response.context["media_files"][0], media)

    @override_settings(WAGTAILMEDIA={"MEDIA_MODEL": "wagtailmedia_tests.CustomMedia"})
    def test_with_custom_model(self):
        response = self.client.get(self.chooser_url)
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.content.decode())
        self.assertEqual(json_data["step"], "chooser")

        # custom form fields should be present
        self.assertIn('name="media-chooser-upload-fancy_caption"', json_data["html"])

        # form media imports should appear on the page
        self.assertIn("wagtailadmin/js/draftail.js", json_data["html"])


class TestTypedMediaChooserView(TestCase, WagtailTestUtils):
    @classmethod
    def setUpTestData(cls):
        audio = models.Media(
            title="Test audio",
            duration=100,
            file=ContentFile("A boring example song", name="song.mp3"),
            type="audio",
        )
        audio.save()

        video = models.Media(
            title="Test video",
            duration=100,
            file=ContentFile("An exciting video", name="video.mp4"),
            type="video",
        )
        video.save()

    def setUp(self):
        self.user = self.login()

    def test_audio_chooser(self):
        response = self.client.get(
            reverse("wagtailmedia:chooser_typed", args=("audio",))
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        json_data = json.loads(response.content.decode("utf-8"))
        self.assertSetEqual(
            set(json_data.keys()),
            {"html", "step", "error_label", "error_message", "tag_autocomplete_url"},
        )
        self.assertTemplateUsed(response, "wagtailmedia/chooser/chooser.html")
        self.assertEqual(json_data["step"], "chooser")
        self.assertEqual(
            json_data["tag_autocomplete_url"], reverse("wagtailadmin_tag_autocomplete")
        )

        html = response.json().get("html")
        for expected in [
            "Test audio",
            'href="#tab-upload-audio"',
            "Upload Audio",
        ]:
            self.assertIn(expected, html)

        for unexpected in [
            "Test video",
            'href="#tab-upload-video"',
            "Upload Video",
        ]:
            self.assertNotIn(unexpected, html)

    def test_video_chooser(self):
        response = self.client.get(
            reverse("wagtailmedia:chooser_typed", args=("video",))
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        html = response.json().get("html")
        for expected in [
            "Test video",
            'href="#tab-upload-video"',
            "Upload Video",
        ]:
            self.assertIn(expected, html)

        for unexpected in [
            "Test audio",
            'href="#tab-upload-audio"',
            "Upload Audio",
        ]:
            self.assertNotIn(unexpected, html)

    def test_typed_chooser_with_invalid_media_type(self):
        with self.assertRaises(NoReverseMatch):
            self.client.get(
                reverse("wagtailmedia:chooser_typed", args=("subspace-transmission",))
            )


class TestMediaChooserViewPermissions(TestCase, WagtailTestUtils):
    @classmethod
    def setUpTestData(cls):
        add_media_permission = Permission.objects.get(
            content_type__app_label="wagtailmedia", codename="add_media"
        )
        admin_permission = Permission.objects.get(
            content_type__app_label="wagtailadmin", codename="access_admin"
        )

        cls.root_collection = Collection.get_first_root_node()
        cls.evil_plans_collection = cls.root_collection.add_child(name="Evil plans")

        conspirators_group = Group.objects.create(name="Evil conspirators")
        conspirators_group.permissions.add(admin_permission)
        GroupCollectionPermission.objects.create(
            group=conspirators_group,
            collection=cls.evil_plans_collection,
            permission=add_media_permission,
        )

        user = get_user_model().objects.create_user(
            username="moriarty", email="moriarty@example.com", password="password"
        )
        user.groups.add(conspirators_group)

        media = models.Media(
            title="Test",
            duration=100,
            file=ContentFile("A boring song", name="test-song.mp3"),
            type="audio",
            collection=cls.root_collection,
        )
        media.save()

        cls.chooser_url = reverse("wagtailmedia:chooser")

    def test_all_permissions_views_root_media(self):
        self.login()

        response = self.client.get(
            self.chooser_url,
            {"collection_id": self.root_collection.id, "q": "test-song.mp3"},
        )
        self.assertIn("test-song.mp3", str(response.content))

    def test_single_collection_permissions_views_nothing(self):
        self.client.login(username="moriarty", password="password")
        response = self.client.get(
            self.chooser_url, {"collection_id": self.root_collection.id}
        )

        media_add_url = reverse("wagtailmedia:add", args=("media",))
        self.assertContains(
            response,
            f'You haven\'t uploaded any media. Why not <a href="{media_add_url}">upload one now</a>',
        )

    def test_upload_permission(self):
        user = get_user_model().objects.create_user(
            username="user", email="user@example.com", password="password"
        )
        user.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="wagtailadmin", codename="access_admin"
            )
        )
        user.save()

        self.login(user)

        response = self.client.get(self.chooser_url)
        self.assertEqual(response.context["uploadforms"], {})


class TestMediaChooserChosenView(TestCase, WagtailTestUtils):
    @classmethod
    def setUpTestData(cls):
        cls.media = models.Media.objects.create(
            title="Test media", file="media.mp3", duration=100
        )

    def setUp(self):
        self.login()

    def test_simple(self):
        response = self.client.get(
            reverse("wagtailmedia:media_chosen", args=(self.media.id,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertDictEqual(
            json.loads(response.content.decode("utf-8")),
            {
                "step": "media_chosen",
                "result": {
                    "id": self.media.id,
                    "title": self.media.title,
                    "edit_url": reverse("wagtailmedia:edit", args=[self.media.id]),
                },
            },
        )


class TestMediaChooserUploadView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def test_upload_audio(self):
        response = self.client.post(
            reverse("wagtailmedia:chooser_upload", args=("audio",)),
            {
                "media-chooser-upload-title": "Test audio",
                "media-chooser-upload-file": ContentFile(
                    "A boring example", name="audio.mp3"
                ),
                "media-chooser-upload-duration": "100",
            },
        )

        # Check response
        self.assertEqual(response.status_code, 200)

        # Check that the audio was created
        media_files = models.Media.objects.filter(title="Test audio")
        self.assertEqual(media_files.count(), 1)

        # Test that fields are populated correctly
        media = media_files.first()
        self.assertEqual(media.type, "audio")
        self.assertEqual(media.duration, 100)

    def test_upload_video(self):
        response = self.client.post(
            reverse("wagtailmedia:chooser_upload", args=("video",)),
            {
                "media-chooser-upload-title": "Test video",
                "media-chooser-upload-file": ContentFile(
                    "A boring example", name="video.avi"
                ),
                "media-chooser-upload-duration": "100",
                "media-chooser-upload-width": "640",
                "media-chooser-upload-height": "480",
            },
        )

        # Check response
        self.assertEqual(response.status_code, 200)

        # Check that the video was created
        media_files = models.Media.objects.filter(title="Test video")
        self.assertEqual(media_files.count(), 1)

        # Test that fields are populated correctly
        media = media_files.first()
        self.assertEqual(media.type, "video")
        self.assertEqual(media.duration, 100)
        self.assertEqual(media.width, 640)
        self.assertEqual(media.height, 480)

    def test_upload_no_file_selected(self):
        response = self.client.post(
            reverse("wagtailmedia:chooser_upload", args=("video",)),
            {"media-chooser-upload-title": "Test video"},
        )

        # Shouldn't redirect anywhere
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/chooser/chooser.html")

        # The video form should have an error
        self.assertIn("uploadforms", response.context)
        self.assertIn("video", response.context["uploadforms"])
        video_form = response.context["uploadforms"]["video"]
        self.assertIn("This field is required.", video_form.errors["file"])
        self.assertEqual(video_form.instance.title, "Test video")
        self.assertEqual(video_form.instance.type, "video")

        # the audio form should not have an error
        self.assertIn("audio", response.context["uploadforms"])
        audio_form = response.context["uploadforms"]["audio"]
        self.assertEqual(audio_form.errors, ErrorDict())
        self.assertEqual(audio_form.instance.title, "")
        self.assertEqual(audio_form.instance.type, "audio")

        # try the audio form
        response = self.client.post(
            reverse("wagtailmedia:chooser_upload", args=("audio",)),
            {"media-chooser-upload-title": "Test audio"},
        )
        audio_form = response.context["uploadforms"]["audio"]
        self.assertIn("This field is required.", audio_form.errors["file"])
        self.assertEqual(audio_form.instance.title, "Test audio")
        self.assertEqual(audio_form.instance.type, "audio")
        video_form = response.context["uploadforms"]["video"]
        self.assertEqual(video_form.errors, ErrorDict())
        self.assertEqual(video_form.instance.title, "")
        self.assertEqual(video_form.instance.type, "video")

    @override_settings(
        STORAGES={
            "default": {
                "BACKEND": "wagtail.test.dummy_external_storage.DummyExternalStorage",
            },
        }
    )
    def test_upload_with_external_storage(self):
        response = self.client.post(
            reverse("wagtailmedia:chooser_upload", args=("video",)),
            {
                "media-chooser-upload-title": "Test video",
                "media-chooser-upload-file": ContentFile(
                    "A boring example", name="video.avi"
                ),
                "media-chooser-upload-duration": "100",
            },
        )

        # Check response
        self.assertEqual(response.status_code, 200)

        # Check that the video was created
        self.assertTrue(models.Media.objects.filter(title="Test video").exists())

    def test_none_field_errors_are_being_rendered(self):
        response = self.client.post(
            reverse("wagtailmedia:chooser_upload", args=("video",)),
            {
                "media-chooser-upload-title": "Test video",
                "media-chooser-upload-file": ContentFile(
                    "A boring example", name="video.pdf"
                ),
            },
        )

        # Check response
        self.assertEqual(response.status_code, 200)

        # The video form should have an error
        self.assertIn("uploadforms", response.context)
        self.assertIn("video", response.context["uploadforms"])
        video_form = response.context["uploadforms"]["video"]

        non_field_errors = video_form.non_field_errors()
        self.assertGreater(len(non_field_errors), 0)

        json_data = json.loads(response.content.decode("utf-8"))

        for error in non_field_errors:
            self.assertIn(error, json_data["html"])


# TODO: Remove once support for Wagtail < 4.1 is dropped
@override_settings(WAGTAIL_USAGE_COUNT_ENABLED=True)
class TestUsageCount(TestCase, WagtailTestUtils):
    fixtures = ["test.json"]

    def setUp(self):
        self.login()

    def test_unused_media_usage_count(self):
        media = models.Media.objects.get(id=1)
        self.assertEqual(media.get_usage().count(), 0)

    def test_used_media_usage_count(self):
        media = models.Media.objects.get(id=1)
        page = EventPage.objects.get(id=3)
        with self.captureOnCommitCallbacks(execute=True):
            event_page_related_link = EventPageRelatedMedia()
            event_page_related_link.page = page
            event_page_related_link.link_media = media
            event_page_related_link.save()
        self.assertEqual(media.get_usage().count(), 1)

    def test_usage_count_appears(self):
        media = models.Media.objects.get(id=1)
        page = EventPage.objects.get(id=3)
        with self.captureOnCommitCallbacks(execute=True):
            event_page_related_link = EventPageRelatedMedia()
            event_page_related_link.page = page
            event_page_related_link.link_media = media
            event_page_related_link.save()
        response = self.client.get(reverse("wagtailmedia:edit", args=(1,)))
        self.assertContains(response, "Used 1 time")

    def test_usage_count_zero_appears(self):
        response = self.client.get(reverse("wagtailmedia:edit", args=(1,)))
        self.assertContains(response, "Used 0 times")
