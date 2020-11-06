# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def get_media_permissions(apps):
    # return a queryset of the 'add_media' and 'change_media' permissions
    Permission = apps.get_model("auth.Permission")
    ContentType = apps.get_model("contenttypes.ContentType")

    media_content_type, _created = ContentType.objects.get_or_create(
        model="media",
        app_label="wagtailmedia",
    )
    return Permission.objects.filter(
        content_type=media_content_type, codename__in=["add_media", "change_media"]
    )


def copy_media_permissions_to_collections(apps, schema_editor):
    Collection = apps.get_model("wagtailcore.Collection")
    Group = apps.get_model("auth.Group")
    GroupCollectionPermission = apps.get_model("wagtailcore.GroupCollectionPermission")

    root_collection = Collection.objects.get(depth=1)

    for permission in get_media_permissions(apps):
        for group in Group.objects.filter(permissions=permission):
            GroupCollectionPermission.objects.create(
                group=group, collection=root_collection, permission=permission
            )


def remove_media_permissions_from_collections(apps, schema_editor):
    GroupCollectionPermission = apps.get_model("wagtailcore.GroupCollectionPermission")
    media_permissions = get_media_permissions(apps)

    GroupCollectionPermission.objects.filter(permission__in=media_permissions).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailmedia", "0002_initial_data"),
        ("wagtailcore", "0026_group_collection_permission"),
    ]

    operations = [
        migrations.RunPython(
            copy_media_permissions_to_collections,
            remove_media_permissions_from_collections,
        ),
    ]
