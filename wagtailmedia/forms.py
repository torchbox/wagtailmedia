from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.forms.models import modelform_factory
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from wagtail import VERSION as WAGTAIL_VERSION
from wagtail.admin import widgets

from wagtailmedia.models import Media
from wagtailmedia.permissions import permission_policy as media_permission_policy


if WAGTAIL_VERSION < (2, 5):
    from wagtail.admin.forms import (
        BaseCollectionMemberForm,
        collection_member_permission_formset_factory,
    )
else:
    from wagtail.admin.forms.collections import (
        BaseCollectionMemberForm,
        collection_member_permission_formset_factory,
    )


class BaseMediaForm(BaseCollectionMemberForm):
    class Meta:
        widgets = {
            "tags": widgets.AdminTagWidget,
            "file": forms.FileInput,
            "thumbnail": forms.ClearableFileInput,
        }

    permission_policy = media_permission_policy

    def __init__(self, *args, **kwargs):
        super(BaseMediaForm, self).__init__(*args, **kwargs)

        if self.instance.type == "audio":
            for name in ("width", "height"):
                # these fields might be editable=False so verify before accessing
                if name in self.fields:
                    del self.fields[name]


def get_media_base_form():
    base_form_override = getattr(settings, "WAGTAILMEDIA_MEDIA_FORM_BASE", "")
    if base_form_override:
        base_form = import_string(base_form_override)
    else:
        base_form = BaseMediaForm
    return base_form


media_base_form = get_media_base_form()


def get_media_form(model):
    fields = model.admin_form_fields
    if "collection" not in fields:
        # force addition of the 'collection' field, because leaving it out can
        # cause dubious results when multiple collections exist (e.g adding the
        # media to the root collection where the user may not have permission) -
        # and when only one collection exists, it will get hidden anyway.
        fields = list(fields) + ["collection"]

    return modelform_factory(
        model,
        form=media_base_form,
        fields=fields,
    )


GroupMediaPermissionFormSet = collection_member_permission_formset_factory(
    Media,
    [
        ("add_media", _("Add"), _("Add/edit media you own")),
        ("change_media", _("Edit"), _("Edit any media")),
    ],
    "wagtailmedia/permissions/includes/media_permissions_formset.html",
)
