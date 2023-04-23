from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import Column
from wagtail.admin.views.generic.chooser import (
    ChooseResultsView,
    ChooseView,
    ChosenView,
)
from wagtail.admin.viewsets.chooser import ChooserViewSet

from ..forms import get_media_form
from ..models import get_media_model
from ..permissions import permission_policy


Media = get_media_model()


class MediaChooserMixin:
    construct_queryset_hook_name = "construct_media_chooser_queryset"

    def get_object_list(self):
        return (
            permission_policy.instances_user_has_any_permission_for(
                self.request.user, ["choose"]
            )
            .select_related("collection")
            .only("title", "file", "type", "collection__name", "created_at")
        )

    @property
    def columns(self):
        return super().columns + [
            Column("file", label="File", accessor="file"),
            Column("type", label="Type", accessor="type"),
            Column("collection", label="Collection", accessor="collection"),
            Column("created_at", label="Uploaded", accessor="created_at"),
        ]

    def get_filter_form(self):
        FilterForm = self.get_filter_form_class()
        return FilterForm(self.request.GET, collections=self.collections)

    @cached_property
    def collections(self):
        collections = self.permission_policy.collections_user_has_permission_for(
            self.request.user, "choose"
        )
        if len(collections) < 2:
            return None

        return collections

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["collections"] = self.collections
        return context


class MediaChooseView(MediaChooserMixin, ChooseView):
    pass


class MediaChooseResultsView(MediaChooserMixin, ChooseResultsView):
    pass


class MediaChosenView(ChosenView):
    def get_object(self, pk):
        return Media.objects.only("title", "thumbnail").get(pk=pk)

    def get_chosen_response_data(self, media_item, preview_image_filter="max-165x165"):
        """
        Given a media item, return the json data to pass back to the image chooser panel
        """
        response_data = super().get_chosen_response_data(media_item)
        if not media_item.thumbnail:
            return response_data

        preview_image = media_item.thumbnail
        response_data["preview"] = {
            "url": preview_image.url,
            "width": 128,
            "height": 128,
        }
        return response_data


class MediaChooserViewSet(ChooserViewSet):
    choose_view_class = MediaChooseView
    chosen_view_class = MediaChosenView
    choose_results_view_class = MediaChooseResultsView
    creation_form_class = get_media_form(Media)
    permission_policy = permission_policy

    icon = "media"
    choose_one_text = _("Choose a media item")
    choose_another_text = _("Choose another media item")
    edit_item_text = _("Edit this media item")
    creation_tab_label = _("Upload")
    create_action_label = _("Upload")
    create_action_clicked_label = _("Uploading…")
    form_fields = ["type", "title", "file", "collection", "thumbnail"]


media_chooser_viewset = MediaChooserViewSet(
    "media_chooser",
    model=Media,
    url_prefix="media/chooser",
)
