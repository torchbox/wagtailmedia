from wagtail import VERSION as WAGTAIL_VERSION

from wagtailmedia.models import Media, get_media_model

if WAGTAIL_VERSION < (2, 0):
    from wagtail.wagtailcore.permission_policies.collections import (
        CollectionOwnershipPermissionPolicy
    )
else:
    from wagtail.core.permission_policies.collections import (
        CollectionOwnershipPermissionPolicy
    )


permission_policy = CollectionOwnershipPermissionPolicy(
    get_media_model(),
    auth_model=Media,
    owner_field_name='uploaded_by_user'
)
