__version__ = "0.18.1"

from django.core.exceptions import ImproperlyConfigured


def get_media_model():
    from django.apps import apps

    from wagtailmedia.settings import wagtailmedia_settings

    try:
        return apps.get_model(wagtailmedia_settings.MEDIA_MODEL, require_ready=False)
    except ValueError as e:
        raise ImproperlyConfigured(
            "WAGTAILMEDIA[\"MEDIA_MODEL\"] must be of the form 'app_label.model_name'"
        ) from e
    except LookupError as e:
        raise ImproperlyConfigured(
            f"WAGTAILMEDIA[\"MEDIA_MODEL\"] refers to model '{wagtailmedia_settings.MEDIA_MODEL}' that has not been installed"
        ) from e


def get_permission_policy():
    from wagtail.permission_policies.collections import (
        CollectionOwnershipPermissionPolicy,
    )

    return CollectionOwnershipPermissionPolicy(
        get_media_model(),
        auth_model="wagtailmedia.Media",
        owner_field_name="uploaded_by_user",
    )
