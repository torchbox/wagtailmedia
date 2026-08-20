from django.utils.functional import cached_property
from wagtail.admin.auth import PermissionPolicyChecker

from wagtailmedia.models import get_media_model


def get_permission_policy():
    from wagtail.permission_policies.collections import (
        CollectionOwnershipPermissionPolicy,
    )

    return CollectionOwnershipPermissionPolicy(
        get_media_model(),
        auth_model="wagtailmedia.Media",
        owner_field_name="uploaded_by_user",
    )


# TODO: remove when dropping support for Wagtail < 8.0
permission_policy = get_permission_policy()


class MediaPermissionPolicyChecker(PermissionPolicyChecker):
    def __init__(self):
        # Provide policy via a cached property so we can retrieve it from the
        # registry at runtime, rather than at import time.
        ...

    @cached_property
    def policy(self):
        return get_permission_policy()
