from wagtail import VERSION as WAGTAIL_VERSION


if WAGTAIL_VERSION >= (3, 0):
    from wagtail.permission_policies.collections import (
        CollectionOwnershipPermissionPolicy,
    )
else:
    from wagtail.core.permission_policies.collections import (
        CollectionOwnershipPermissionPolicy,
    )

from wagtailmedia.models import Media, get_media_model


permission_policy = CollectionOwnershipPermissionPolicy(
    get_media_model(), auth_model=Media, owner_field_name="uploaded_by_user"
)
