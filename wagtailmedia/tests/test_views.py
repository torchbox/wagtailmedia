from __future__ import unicode_literals

import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.files.base import ContentFile
from django.test import TestCase
from django.test.utils import override_settings

from six import b
from wagtail.tests.utils import WagtailTestUtils

from wagtailmedia import models
from wagtailmedia.tests.testapp.models import EventPage, EventPageRelatedMedia

try:
    from django.urls import reverse
except ImportError:  # fallback for older Django
    from django.core.urlresolvers import reverse

try:
    from wagtail.core.models import (
        Collection, GroupCollectionPermission, Page
    )
except ImportError:  # fallback for wagtail <2.0
    from wagtail.wagtailcore.models import (
        Collection, GroupCollectionPermission, Page
    )


class TestMediaIndexView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def test_simple(self):
        response = self.client.get(reverse('wagtailmedia:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailmedia/media/index.html')
        self.assertContains(response, "Add audio")
        self.assertContains(response, "Add video")

    def test_search(self):
        response = self.client.get(reverse('wagtailmedia:index'), {'q': "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['query_string'], "Hello")

    @staticmethod
    def make_media():
        fake_file = ContentFile(b("A boring example song"))
        fake_file.name = 'song.mp3'

        for i in range(50):
            media = models.Media(
                title="Test " + str(i),
                duration=100 + i,
                file=fake_file,
                type='audio',
            )
            media.save()

    def test_pagination(self):
        self.make_media()

        response = self.client.get(reverse('wagtailmedia:index'), {'p': 2})

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailmedia/media/index.html')

        # Check that we got the correct page
        self.assertEqual(response.context['media_files'].number, 2)

    def test_pagination_invalid(self):
        self.make_media()

        response = self.client.get(reverse('wagtailmedia:index'), {'p': 'Hello World!'})

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailmedia/media/index.html')

        # Check that we got page one
        self.assertEqual(response.context['media_files'].number, 1)

    def test_pagination_out_of_range(self):
        self.make_media()

        response = self.client.get(reverse('wagtailmedia:index'), {'p': 99999})

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailmedia/media/index.html')

        # Check that we got the last page
        self.assertEqual(response.context['media_files'].number, response.context['media_files'].paginator.num_pages)

    def test_ordering(self):
        orderings = ['title', '-created_at']
        for ordering in orderings:
            response = self.client.get(reverse('wagtailmedia:index'), {'ordering': ordering})
            self.assertEqual(response.status_code, 200)


class TestMediaAddView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def test_get_audio(self):
        response = self.client.get(reverse('wagtailmedia:add', args=('audio', )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailmedia/media/add.html')

        # as standard, only the root collection exists and so no 'Collection' option
        # is displayed on the form
        self.assertNotContains(response, '<label for="id_collection">')
        self.assertContains(response, 'Add audio')
        self.assertContains(
            response,
            '<form action="{0}" method="POST" enctype="multipart/form-data" novalidate>'.format(
                reverse('wagtailmedia:add', args=('audio',))
            ),
            count=1
        )

    def test_get_video(self):
        response = self.client.get(reverse('wagtailmedia:add', args=('video', )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailmedia/media/add.html')
        self.assertContains(response, 'Add video')
        self.assertContains(
            response,
            '<form action="{0}" method="POST" enctype="multipart/form-data" novalidate>'.format(
                reverse('wagtailmedia:add', args=('video',))
            ),
            count=1
        )

        # as standard, only the root collection exists and so no 'Collection' option
        # is displayed on the form
        self.assertNotContains(response, '<label for="id_collection">')

    def test_get_audio_with_collections(self):
        root_collection = Collection.get_first_root_node()
        root_collection.add_child(name="Evil plans")

        response = self.client.get(reverse('wagtailmedia:add', args=('audio', )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailmedia/media/add.html')

        self.assertContains(response, '<label for="id_collection">')
        self.assertContains(response, "Evil plans")
        self.assertContains(response, 'Add audio')
        self.assertContains(
            response,
            '<form action="{0}" method="POST" enctype="multipart/form-data" novalidate>'.format(
                reverse('wagtailmedia:add', args=('audio',))
            ),
            count=1
        )

    def test_get_video_with_collections(self):
        root_collection = Collection.get_first_root_node()
        root_collection.add_child(name="Evil plans")

        response = self.client.get(reverse('wagtailmedia:add', args=('video', )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailmedia/media/add.html')

        self.assertContains(response, '<label for="id_collection">')
        self.assertContains(response, "Evil plans")
        self.assertContains(response, 'Add video')
        self.assertContains(
            response,
            '<form action="{0}" method="POST" enctype="multipart/form-data" novalidate>'.format(
                reverse('wagtailmedia:add', args=('video',))
            ),
            count=1
        )

    def test_post_audio(self):
        # Build a fake file
        fake_file = ContentFile(b("A boring example song"))
        fake_file.name = 'song.mp3'

        # Submit
        post_data = {
            'title': "Test media",
            'file': fake_file,
            'duration': 100,
        }
        response = self.client.post(reverse('wagtailmedia:add', args=('audio', )), post_data)

        # User should be redirected back to the index
        self.assertRedirects(response, reverse('wagtailmedia:index'))

        # Media should be created, and be placed in the root collection
        self.assertTrue(models.Media.objects.filter(title="Test media").exists())
        root_collection = Collection.get_first_root_node()

        media = models.Media.objects.get(title="Test media")
        self.assertEqual(media.collection, root_collection)
        self.assertEqual(media.type, 'audio')

    def test_post_video(self):
        # Build a fake file
        fake_file = ContentFile(b("A boring example movie"))
        fake_file.name = 'movie.mp4'

        # Submit
        post_data = {
            'title': "Test media",
            'file': fake_file,
            'duration': 100,
            'width': 720,
            'height': 480,
        }
        response = self.client.post(reverse('wagtailmedia:add', args=('video', )), post_data)

        # User should be redirected back to the index
        self.assertRedirects(response, reverse('wagtailmedia:index'))

        # Media should be created, and be placed in the root collection
        self.assertTrue(models.Media.objects.filter(title="Test media").exists())
        root_collection = Collection.get_first_root_node()
        media = models.Media.objects.get(title="Test media")
        self.assertEqual(media.collection, root_collection)
        self.assertEqual(media.type, 'video')

    def test_post_audio_with_collections(self):
        root_collection = Collection.get_first_root_node()
        evil_plans_collection = root_collection.add_child(name="Evil plans")

        # Build a fake file
        fake_file = ContentFile(b("A boring example song"))
        fake_file.name = 'song.mp3'

        # Submit
        post_data = {
            'title': "Test media",
            'file': fake_file,
            'duration': 100,
            'collection': evil_plans_collection.id,
        }
        response = self.client.post(reverse('wagtailmedia:add', args=('audio', )), post_data)

        # User should be redirected back to the index
        self.assertRedirects(response, reverse('wagtailmedia:index'))

        # Media should be created, and be placed in the Evil Plans collection
        self.assertTrue(models.Media.objects.filter(title="Test media").exists())

        media = models.Media.objects.get(title="Test media")
        self.assertEqual(media.collection, evil_plans_collection)
        self.assertEqual(media.type, 'audio')

    def test_post_video_with_collections(self):
        root_collection = Collection.get_first_root_node()
        evil_plans_collection = root_collection.add_child(name="Evil plans")

        # Build a fake file
        fake_file = ContentFile(b("A boring example movie"))
        fake_file.name = 'movie.mp3'

        # Submit
        post_data = {
            'title': "Test media",
            'file': fake_file,
            'duration': 100,
            'collection': evil_plans_collection.id,
        }
        response = self.client.post(reverse('wagtailmedia:add', args=('video', )), post_data)

        # User should be redirected back to the index
        self.assertRedirects(response, reverse('wagtailmedia:index'))

        # Media should be created, and be placed in the Evil Plans collection
        self.assertTrue(models.Media.objects.filter(title="Test media").exists())

        media = models.Media.objects.get(title="Test media")
        self.assertEqual(media.collection, evil_plans_collection)
        self.assertEqual(media.type, 'video')


class TestMediaAddViewWithLimitedCollectionPermissions(TestCase, WagtailTestUtils):
    def setUp(self):
        add_media_permission = Permission.objects.get(
            content_type__app_label='wagtailmedia', codename='add_media'
        )
        admin_permission = Permission.objects.get(
            content_type__app_label='wagtailadmin', codename='access_admin'
        )

        root_collection = Collection.get_first_root_node()
        self.evil_plans_collection = root_collection.add_child(name="Evil plans")

        conspirators_group = Group.objects.create(name="Evil conspirators")
        conspirators_group.permissions.add(admin_permission)
        GroupCollectionPermission.objects.create(
            group=conspirators_group,
            collection=self.evil_plans_collection,
            permission=add_media_permission
        )

        user = get_user_model().objects.create_user(
            username='moriarty',
            email='moriarty@example.com',
            password='password'
        )
        user.groups.add(conspirators_group)

        self.client.login(username='moriarty', password='password')

    def test_get_audio(self):
        response = self.client.get(reverse('wagtailmedia:add', args=('audio', )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailmedia/media/add.html')

        # user only has access to one collection, so no 'Collection' option
        # is displayed on the form
        self.assertNotContains(response, '<label for="id_collection">')
        self.assertContains(response, 'Add audio')
        self.assertContains(
            response,
            '<form action="{0}" method="POST" enctype="multipart/form-data" novalidate>'.format(
                reverse('wagtailmedia:add', args=('audio',))
            ),
            count=1
        )

    def test_get_video(self):
        response = self.client.get(reverse('wagtailmedia:add', args=('video', )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailmedia/media/add.html')

        # user only has access to one collection, so no 'Collection' option
        # is displayed on the form
        self.assertNotContains(response, '<label for="id_collection">')
        self.assertContains(response, 'Add video')
        self.assertContains(
            response,
            '<form action="{0}" method="POST" enctype="multipart/form-data" novalidate>'.format(
                reverse('wagtailmedia:add', args=('video',))
            ),
            count=1
        )

    def test_post_audio(self):
        # Build a fake file
        fake_file = ContentFile(b("A boring example song"))
        fake_file.name = 'song.mp3'

        # Submit
        post_data = {
            'title': "Test media",
            'file': fake_file,
            'duration': 100,
        }
        response = self.client.post(reverse('wagtailmedia:add', args=('audio', )), post_data)

        # User should be redirected back to the index
        self.assertRedirects(response, reverse('wagtailmedia:index'))

        # Media should be created with type 'audio' and in the 'evil plans' collection,
        # despite there being no collection field in the form, because that's the
        # only one the user has access to
        self.assertTrue(models.Media.objects.filter(title="Test media").exists())
        media = models.Media.objects.get(title="Test media")
        self.assertEqual(media.collection, self.evil_plans_collection)
        self.assertEqual(media.type, 'audio')

    def test_post_video(self):
        # Build a fake file
        fake_file = ContentFile(b("A boring example movie"))
        fake_file.name = 'movie.mp4'

        # Submit
        post_data = {
            'title': "Test media",
            'file': fake_file,
            'duration': 100,
        }
        response = self.client.post(reverse('wagtailmedia:add', args=('video', )), post_data)

        # User should be redirected back to the index
        self.assertRedirects(response, reverse('wagtailmedia:index'))

        # Media should be created with type 'video' and in the 'evil plans' collection,
        # despite there being no collection field in the form, because that's the
        # only one the user has access to
        self.assertTrue(models.Media.objects.filter(title="Test media").exists())
        media = models.Media.objects.get(title="Test media")
        self.assertEqual(media.collection, self.evil_plans_collection)
        self.assertEqual(media.type, 'video')


class TestMediaEditView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

        # Build a fake file
        fake_file = ContentFile(b("A boring example song"))
        fake_file.name = 'song.mp3'

        # Create a media to edit
        self.media = models.Media.objects.create(title="Test media", file=fake_file, duration=100)

    def test_simple(self):
        response = self.client.get(reverse('wagtailmedia:edit', args=(self.media.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailmedia/media/edit.html')

    def test_post(self):
        # Build a fake file
        fake_file = ContentFile(b("A boring example song"))
        fake_file.name = 'song.mp3'

        # Submit title change
        post_data = {
            'title': "Test media changed!",
            'file': fake_file,
            'duration': 100,
        }
        response = self.client.post(reverse('wagtailmedia:edit', args=(self.media.id,)), post_data)

        # User should be redirected back to the index
        self.assertRedirects(response, reverse('wagtailmedia:index'))

        # Media title should be changed
        self.assertEqual(models.Media.objects.get(id=self.media.id).title, "Test media changed!")

    def test_with_missing_source_file(self):
        # Build a fake file
        fake_file = ContentFile(b("An ephemeral media"))
        fake_file.name = 'to-be-deleted.mp3'

        # Create a new media to delete the source for
        media = models.Media.objects.create(title="Test missing source media", file=fake_file, duration=100)
        media.file.delete(False)

        response = self.client.get(reverse('wagtailmedia:edit', args=(media.id,)), {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailmedia/media/edit.html')

        self.assertContains(response, 'File not found')


class TestMediaDeleteView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

        # Create a media to delete
        self.media = models.Media.objects.create(title="Test media", duration=100)

    def test_simple(self):
        response = self.client.get(reverse('wagtailmedia:delete', args=(self.media.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailmedia/media/confirm_delete.html')

    def test_delete(self):
        # Submit title change
        post_data = {
            'foo': 'bar'
        }
        response = self.client.post(reverse('wagtailmedia:delete', args=(self.media.id,)), post_data)

        # User should be redirected back to the index
        self.assertRedirects(response, reverse('wagtailmedia:index'))

        # Media should be deleted
        self.assertFalse(models.Media.objects.filter(id=self.media.id).exists())

    @override_settings(WAGTAIL_USAGE_COUNT_ENABLED=True)
    def test_usage_link(self):
        response = self.client.get(reverse('wagtailmedia:delete', args=(self.media.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailmedia/media/confirm_delete.html')
        self.assertIn('Used 0 times', str(response.content))


class TestMediaChooserView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def test_simple(self):
        response = self.client.get(reverse('wagtailmedia:chooser'))
        self.assertEqual(response.status_code, 200)

        response_json = json.loads(response.content.decode())
        self.assertEqual(response_json['step'], 'chooser')

        self.assertTemplateUsed(response, 'wagtailmedia/chooser/chooser.html')

    def test_search(self):
        response = self.client.get(reverse('wagtailmedia:chooser'), {'q': "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['query_string'], "Hello")

    @staticmethod
    def make_media():
        fake_file = ContentFile(b("A boring example song"))
        fake_file.name = 'song.mp3'

        for i in range(50):
            media = models.Media(
                title="Test " + str(i),
                duration=100 + i,
                file=fake_file,
                type='audio',
            )
            media.save()

    def test_pagination(self):
        self.make_media()

        response = self.client.get(reverse('wagtailmedia:chooser'), {'p': 2})

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailmedia/media/list.html')

        # Check that we got the correct page
        self.assertEqual(response.context['media_files'].number, 2)

    def test_pagination_invalid(self):
        self.make_media()

        response = self.client.get(reverse('wagtailmedia:chooser'), {'p': 'Hello World!'})

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailmedia/media/list.html')

        # Check that we got page one
        self.assertEqual(response.context['media_files'].number, 1)

    def test_pagination_out_of_range(self):
        self.make_media()

        response = self.client.get(reverse('wagtailmedia:chooser'), {'p': 99999})

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailmedia/media/list.html')

        # Check that we got the last page
        self.assertEqual(response.context['media_files'].number, response.context['media_files'].paginator.num_pages)


class TestMediaChooserChosenView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

        # Create a media to choose
        self.media = models.Media.objects.create(title="Test media", duration=100)

    def test_simple(self):
        response = self.client.get(reverse('wagtailmedia:media_chosen', args=(self.media.id,)))
        self.assertEqual(response.status_code, 200)

        response_json = json.loads(response.content.decode())
        self.assertEqual(response_json['step'], 'media_chosen')

class TestMediaFilenameProperties(TestCase):
    def setUp(self):
        self.media = models.Media(title="Test media", duration=100)
        self.media.file.save('example.mp4', ContentFile("A amazing example music video"))

        self.extensionless_media = models.Media(title="Test media", duration=101)
        self.extensionless_media.file.save('example', ContentFile("A boring example music video"))

    def test_filename(self):
        self.assertEqual('example.mp4', self.media.filename)
        self.assertEqual('example', self.extensionless_media.filename)

    def test_file_extension(self):
        self.assertEqual('mp4', self.media.file_extension)
        self.assertEqual('', self.extensionless_media.file_extension)

    def tearDown(self):
        self.media.delete()
        self.extensionless_media.delete()


class TestUsageCount(TestCase, WagtailTestUtils):
    fixtures = ['test.json']

    def setUp(self):
        self.login()

    @override_settings(WAGTAIL_USAGE_COUNT_ENABLED=True)
    def test_unused_media_usage_count(self):
        media = models.Media.objects.get(id=1)
        self.assertEqual(media.get_usage().count(), 0)

    @override_settings(WAGTAIL_USAGE_COUNT_ENABLED=True)
    def test_used_media_usage_count(self):
        media = models.Media.objects.get(id=1)
        page = EventPage.objects.get(id=3)
        event_page_related_link = EventPageRelatedMedia()
        event_page_related_link.page = page
        event_page_related_link.link_media = media
        event_page_related_link.save()
        self.assertEqual(media.get_usage().count(), 1)

    def test_usage_count_does_not_appear(self):
        media = models.Media.objects.get(id=1)
        page = EventPage.objects.get(id=3)
        event_page_related_link = EventPageRelatedMedia()
        event_page_related_link.page = page
        event_page_related_link.link_media = media
        event_page_related_link.save()
        response = self.client.get(reverse('wagtailmedia:edit',
                                           args=(1,)))
        self.assertNotContains(response, 'Used 1 time')

    @override_settings(WAGTAIL_USAGE_COUNT_ENABLED=True)
    def test_usage_count_appears(self):
        media = models.Media.objects.get(id=1)
        page = EventPage.objects.get(id=3)
        event_page_related_link = EventPageRelatedMedia()
        event_page_related_link.page = page
        event_page_related_link.link_media = media
        event_page_related_link.save()
        response = self.client.get(reverse('wagtailmedia:edit',
                                           args=(1,)))
        self.assertContains(response, 'Used 1 time')

    @override_settings(WAGTAIL_USAGE_COUNT_ENABLED=True)
    def test_usage_count_zero_appears(self):
        response = self.client.get(reverse('wagtailmedia:edit',
                                           args=(1,)))
        self.assertContains(response, 'Used 0 times')


class TestGetUsage(TestCase, WagtailTestUtils):
    fixtures = ['test.json']

    def setUp(self):
        self.login()

    def test_media_get_usage_not_enabled(self):
        media = models.Media.objects.get(id=1)
        self.assertEqual(list(media.get_usage()), [])

    @override_settings(WAGTAIL_USAGE_COUNT_ENABLED=True)
    def test_unused_media_get_usage(self):
        media = models.Media.objects.get(id=1)
        self.assertEqual(list(media.get_usage()), [])

    @override_settings(WAGTAIL_USAGE_COUNT_ENABLED=True)
    def test_used_media_get_usage(self):
        media = models.Media.objects.get(id=1)
        page = EventPage.objects.get(id=3)
        event_page_related_link = EventPageRelatedMedia()
        event_page_related_link.page = page
        event_page_related_link.link_media = media
        event_page_related_link.save()
        self.assertTrue(issubclass(Page, type(media.get_usage()[0])))

    @override_settings(WAGTAIL_USAGE_COUNT_ENABLED=True)
    def test_usage_page(self):
        media = models.Media.objects.get(id=1)
        page = EventPage.objects.get(id=3)
        event_page_related_link = EventPageRelatedMedia()
        event_page_related_link.page = page
        event_page_related_link.link_media = media
        event_page_related_link.save()
        response = self.client.get(reverse('wagtailmedia:media_usage',
                                           args=(1,)))
        self.assertContains(response, 'Christmas')

    @override_settings(WAGTAIL_USAGE_COUNT_ENABLED=True)
    def test_usage_page_no_usage(self):
        response = self.client.get(reverse('wagtailmedia:media_usage',
                                           args=(1,)))
        # There's no usage so there should be no table rows
        self.assertRegex(response.content, b'<tbody>(\s|\n)*</tbody>')
