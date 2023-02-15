from django import VERSION as DJANGO_VERSION
from django.db import migrations


def add_media_permissions_to_admin_groups(apps, schema_editor):
    ContentType = apps.get_model("contenttypes.ContentType")
    Permission = apps.get_model("auth.Permission")
    Group = apps.get_model("auth.Group")

    # Get media permissions
    media_content_type, _created = ContentType.objects.get_or_create(
        model="media",
        app_label="wagtailmedia",
        defaults={"name": "media"} if DJANGO_VERSION < (1, 8) else {},
    )

    add_media_permission, _created = Permission.objects.get_or_create(
        content_type=media_content_type,
        codename="add_media",
        defaults={"name": "Can add media"},
    )
    change_media_permission, _created = Permission.objects.get_or_create(
        content_type=media_content_type,
        codename="change_media",
        defaults={"name": "Can change media"},
    )
    delete_media_permission, _created = Permission.objects.get_or_create(
        content_type=media_content_type,
        codename="delete_media",
        defaults={"name": "Can delete media"},
    )

    # Assign it to Editors and Moderators groups
    for group in Group.objects.filter(name__in=["Editors", "Moderators"]):
        group.permissions.add(
            add_media_permission, change_media_permission, delete_media_permission
        )


def remove_media_permissions(apps, schema_editor):
    """Reverse the above additions of permissions."""
    ContentType = apps.get_model("contenttypes.ContentType")
    Permission = apps.get_model("auth.Permission")
    media_content_type = ContentType.objects.get(
        model="media",
        app_label="wagtailmedia",
    )
    # This cascades to Group
    Permission.objects.filter(
        content_type=media_content_type,
        codename__in=("add_media", "change_media", "delete_media"),
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailmedia", "0001_initial"),
        # Need to run wagtailcores initial data migration to make sure the groups are created
        ("wagtailcore", "0002_initial_data"),
    ]

    operations = [
        migrations.RunPython(
            add_media_permissions_to_admin_groups, remove_media_permissions
        ),
    ]
