from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from utils import create_video
from wagtail.api.v3.tests.base import TestV3Base
from wagtail.models import GroupCollectionPermission
from wagtail.test.utils import WagtailTestUtils
from wagtail.test.utils.wagtail_factories import CollectionFactory


class TestV3MediaBase(TestV3Base, WagtailTestUtils, TestCase):
    def create_media(self, **kwargs):
        return create_video(**kwargs)

    def create_collection(self, name="Test collection", parent=None):
        return CollectionFactory.create(name=name, parent=parent)

    def grant_collection_permission(self, user, collection, codename):
        group = Group.objects.create(
            name=f"{user.get_username()}-{collection.pk}-{codename}"
        )
        user.groups.add(group)
        permission = Permission.objects.get(
            content_type__app_label="wagtailmedia",
            codename=codename,
        )
        GroupCollectionPermission.objects.create(
            group=group,
            collection=collection,
            permission=permission,
        )
