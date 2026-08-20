from django.utils.functional import cached_property
from wagtail.admin.auth import PermissionPolicyChecker

from . import get_permission_policy


# TODO: remove when dropping support for Wagtail < 8.0
permission_policy = get_permission_policy()


class MediaPermissionPolicyChecker(PermissionPolicyChecker):
    def __init__(self):
        # Provide policy via a cached property so we can retrieve it from the
        # registry at runtime, rather than at import time.
        ...

    @cached_property
    def policy(self):
        # TODO: use wagtail.permissions.policy_registry.get_by_type(get_media_model())
        # when dropping support for Wagtail < 8.0
        return get_permission_policy()
