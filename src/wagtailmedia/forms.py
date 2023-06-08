from django import forms
from django.forms.models import modelform_factory
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from wagtail.admin import widgets
from wagtail.admin.forms.collections import (
    BaseCollectionMemberForm,
    CollectionChoiceField,
    collection_member_permission_formset_factory,
)
from wagtail.models import Collection

from wagtailmedia.models import Media
from wagtailmedia.permissions import permission_policy as media_permission_policy
from wagtailmedia.settings import wagtailmedia_settings


# Callback to allow us to override the default form field for the collection field
def formfield_for_dbfield(db_field, **kwargs):
    if db_field.name == "collection":
        return CollectionChoiceField(
            label=_("Collection"),
            queryset=Collection.objects.all(),
            empty_label=None,
            **kwargs,
        )

    # For all other fields, just call its formfield() method.
    return db_field.formfield(**kwargs)


class BaseMediaForm(BaseCollectionMemberForm):
    class Meta:
        widgets = {
            "tags": widgets.AdminTagWidget,
            "file": forms.FileInput,
            "thumbnail": forms.ClearableFileInput,
        }

    permission_policy = media_permission_policy

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.type == "audio":
            for name in ("width", "height"):
                # these fields might be editable=False so verify before accessing
                if name in self.fields:
                    del self.fields[name]


def get_media_base_form():
    base_form_override = wagtailmedia_settings.MEDIA_FORM_BASE
    if base_form_override:
        base_form = import_string(base_form_override)
    else:
        base_form = BaseMediaForm
    return base_form


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
        form=get_media_base_form(),
        fields=fields,
        formfield_callback=formfield_for_dbfield,
    )


GroupMediaPermissionFormSet = collection_member_permission_formset_factory(
    Media,
    [
        ("add_media", _("Add"), _("Add/edit media you own")),
        ("change_media", _("Edit"), _("Edit any media")),
    ],
    "wagtailmedia/permissions/includes/media_permissions_formset.html",
)
