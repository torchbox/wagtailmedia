from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.files.base import ContentFile
from django.test import TestCase
from django.urls import reverse

from wagtail.core.models import Collection, GroupCollectionPermission
from wagtail.tests.utils import WagtailTestUtils

from six import b

from wagtailmedia import models


class TestMediaPermissions(TestCase):
    def setUp(self):
        # Create some user accounts for testing permissions
        User = get_user_model()
        self.user = User.objects.create_user(
            username="user", email="user@email.com", password="password"
        )
        self.owner = User.objects.create_user(
            username="owner", email="owner@email.com", password="password"
        )
        self.editor = User.objects.create_user(
            username="editor", email="editor@email.com", password="password"
        )
        self.editor.groups.add(Group.objects.get(name="Editors"))
        self.administrator = User.objects.create_superuser(
            username="administrator",
            email="administrator@email.com",
            password="password",
        )

        # Owner user must have the add_media permission
        self.adders_group = Group.objects.create(name="Media adders")
        GroupCollectionPermission.objects.create(
            group=self.adders_group,
            collection=Collection.get_first_root_node(),
            permission=Permission.objects.get(codename="add_media"),
        )
        self.owner.groups.add(self.adders_group)

        # Create a media for running tests on
        self.media = models.Media.objects.create(
            title="Test media", duration=100, uploaded_by_user=self.owner
        )

    def test_administrator_can_edit(self):
        self.assertTrue(self.media.is_editable_by_user(self.administrator))

    def test_editor_can_edit(self):
        self.assertTrue(self.media.is_editable_by_user(self.editor))

    def test_owner_can_edit(self):
        self.assertTrue(self.media.is_editable_by_user(self.owner))

    def test_user_cant_edit(self):
        self.assertFalse(self.media.is_editable_by_user(self.user))


class TestEditOnlyPermissions(TestCase, WagtailTestUtils):
    def setUp(self):
        # Build a fake file
        fake_file = ContentFile(b("A boring example song"))
        fake_file.name = "song.mp3"

        self.root_collection = Collection.get_first_root_node()
        self.evil_plans_collection = self.root_collection.add_child(name="Evil plans")
        self.nice_plans_collection = self.root_collection.add_child(name="Nice plans")

        # Create a media to edit
        self.media = models.Media.objects.create(
            title="Test media",
            file=fake_file,
            collection=self.nice_plans_collection,
            duration=100,
        )

        # Create a user with change_media permission but not add_media
        user = get_user_model().objects.create_user(
            username="changeonly", email="changeonly@example.com", password="password"
        )
        change_permission = Permission.objects.get(
            content_type__app_label="wagtailmedia", codename="change_media"
        )
        admin_permission = Permission.objects.get(
            content_type__app_label="wagtailadmin", codename="access_admin"
        )
        self.changers_group = Group.objects.create(name="Media changers")
        GroupCollectionPermission.objects.create(
            group=self.changers_group,
            collection=self.root_collection,
            permission=change_permission,
        )
        user.groups.add(self.changers_group)

        user.user_permissions.add(admin_permission)
        self.assertTrue(self.client.login(username="changeonly", password="password"))

    def test_get_index(self):
        response = self.client.get(reverse("wagtailmedia:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/index.html")

        # user should not get an "Add audio" and "Add video" buttons
        self.assertNotContains(response, "Add audio")
        self.assertNotContains(response, "Add video")

        # user should be able to see media not owned by them
        self.assertContains(response, "Test media")

    def test_search(self):
        response = self.client.get(reverse("wagtailmedia:index"), {"q": "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["query_string"], "Hello")

    def test_get_add(self):
        response = self.client.get(reverse("wagtailmedia:add", args=("audio",)))
        # permission should be denied
        self.assertRedirects(response, reverse("wagtailadmin_home"))

    def test_get_edit(self):
        response = self.client.get(reverse("wagtailmedia:edit", args=(self.media.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/edit.html")

        # media can only be moved to collections you have add permission for,
        # so the 'collection' field is not available here
        self.assertNotContains(response, '<label for="id_collection">')

        # if the user has add permission on a different collection,
        # they should have option to move the media
        add_permission = Permission.objects.get(
            content_type__app_label="wagtailmedia", codename="add_media"
        )
        GroupCollectionPermission.objects.create(
            group=self.changers_group,
            collection=self.evil_plans_collection,
            permission=add_permission,
        )
        response = self.client.get(reverse("wagtailmedia:edit", args=(self.media.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<label for="id_collection">')
        self.assertContains(response, "Nice plans")
        self.assertContains(response, "Evil plans")

    def test_post_edit(self):
        # Submit title change
        response = self.client.post(
            reverse("wagtailmedia:edit", args=(self.media.id,)),
            {
                "title": "Test media changed!",
                "file": "",
                "duration": 100,
            },
        )

        # User should be redirected back to the index
        self.assertRedirects(response, reverse("wagtailmedia:index"))

        # Media title should be changed
        self.assertEqual(
            models.Media.objects.get(id=self.media.id).title, "Test media changed!"
        )

        # collection should be unchanged
        self.assertEqual(
            models.Media.objects.get(id=self.media.id).collection,
            self.nice_plans_collection,
        )

        # if the user has add permission on a different collection,
        # they should have option to move the media
        add_permission = Permission.objects.get(
            content_type__app_label="wagtailmedia", codename="add_media"
        )
        GroupCollectionPermission.objects.create(
            group=self.changers_group,
            collection=self.evil_plans_collection,
            permission=add_permission,
        )

        self.client.post(
            reverse("wagtailmedia:edit", args=(self.media.id,)),
            {
                "title": "Test media changed!",
                "collection": self.evil_plans_collection.id,
                "file": "",
                "duration": 100,
            },
        )
        self.assertEqual(
            models.Media.objects.get(id=self.media.id).collection,
            self.evil_plans_collection,
        )

    def test_get_delete(self):
        response = self.client.get(
            reverse("wagtailmedia:delete", args=(self.media.id,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailmedia/media/confirm_delete.html")
