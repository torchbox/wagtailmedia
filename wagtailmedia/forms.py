from __future__ import unicode_literals

from django import forms
from django.forms.models import modelform_factory
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailadmin import widgets
from wagtail.wagtailadmin.forms import (
    BaseCollectionMemberForm, collection_member_permission_formset_factory
)

from wagtailmedia.models import Media
from wagtailmedia.permissions import \
    permission_policy as media_permission_policy


class BaseMediaForm(BaseCollectionMemberForm):
    permission_policy = media_permission_policy

    def __init__(self, *args, **kwargs):
        super(BaseMediaForm, self).__init__(*args, **kwargs)

        # We will need to exclude duration, width, height, thumbnail
        # if we would get this information from files metadata

        if self.instance.type == 'audio':
            del self.fields['width']
            del self.fields['height']
            del self.fields['thumbnail']


def get_media_form(model):
    fields = model.admin_form_fields
    if 'collection' not in fields:
        # force addition of the 'collection' field, because leaving it out can
        # cause dubious results when multiple collections exist (e.g adding the
        # media to the root collection where the user may not have permission) -
        # and when only one collection exists, it will get hidden anyway.
        fields = list(fields) + ['collection']

    return modelform_factory(
        model,
        form=BaseMediaForm,
        fields=fields,
        widgets={
            'tags': widgets.AdminTagWidget,
            'file': forms.FileInput(),
            'thumbnail': forms.FileInput(),
        })


GroupMediaPermissionFormSet = collection_member_permission_formset_factory(
    Media,
    [
        ('add_media', _("Add"), _("Add/edit media you own")),
        ('change_media', _("Edit"), _("Edit any media")),
    ],
    'wagtailmedia/permissions/includes/media_permissions_formset.html'
)
