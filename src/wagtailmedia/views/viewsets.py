from typing import TYPE_CHECKING, Any, ClassVar

from django.db.models import QuerySet
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import Column, DateColumn, DownloadColumn
from wagtail.admin.views.generic.chooser import (
    BaseChooseView,
    ChooseResultsViewMixin,
    ChooseViewMixin,
    ChosenView,
    CreationFormMixin,
)
from wagtail.admin.viewsets.chooser import ChooserViewSet

from wagtailmedia.models import get_media_model
from wagtailmedia.permissions import permission_policy


if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

    from wagtailmedia.models import Media as MediaBase


Media: "MediaBase" = get_media_model()


class MediaCreationFormMixin(CreationFormMixin):
    creation_tab_id = "upload"

    def get_creation_form_class(self):
        from wagtailmedia.forms import get_media_form

        return get_media_form(self.model)

    def get_creation_form_kwargs(self):
        kwargs = super().get_creation_form_kwargs()
        kwargs.update(
            {
                "user": self.request.user,
                "prefix": "media-chooser-upload",
            }
        )
        if self.request.method in ("POST", "PUT"):
            kwargs["instance"] = self.model(uploaded_by_user=self.request.user)

        return kwargs


class BaseMediaChooseView(BaseChooseView):
    per_page = 10
    ordering = "-created_at"
    construct_queryset_hook_name: ClassVar[str] = "construct_media_chooser_queryset"

    def get_object_list(self) -> QuerySet["MediaBase"]:
        return (
            permission_policy.instances_user_has_any_permission_for(
                self.request.user, ["choose"]
            )
            .select_related("collection")
            .only("title", "file", "type", "collection__name", "created_at")
        )

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

    @property
    def columns(self) -> list[Column]:
        columns = super().columns + [
            DownloadColumn("file", label="File", accessor="file"),
            Column("type", label="Type", accessor="type"),
            Column("collection", label="Collection", accessor="collection"),
            DateColumn("created_at", label="Uploaded", accessor="created_at"),
        ]

        if self.collections:
            columns.insert(2, Column("collection", label=_("Collection")))

        return columns

    def get(self, request: "HttpRequest") -> "HttpResponse":
        self.model = Media
        return super().get(request)


class MediaChooseViewMixin(ChooseViewMixin):
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["collections"] = self.collections
        return context


class MediaChooseView(
    MediaChooseViewMixin, MediaCreationFormMixin, BaseMediaChooseView
): ...


class MediaChooseResultsView(
    ChooseResultsViewMixin, MediaCreationFormMixin, BaseMediaChooseView
): ...


class MediaChosenView(ChosenView):
    def get_object(self, pk: int) -> "MediaBase":
        return Media.objects.only("title", "thumbnail").get(pk=pk)

    def get_chosen_response_data(
        self, media_item: "MediaBase", preview_image_filter: str = "max-165x165"
    ) -> dict[str, Any]:
        """
        Given a media item, return the json data to pass back to the image chooser panel
        """
        response_data = super().get_chosen_response_data(media_item)
        if not media_item.thumbnail:
            return response_data

        if preview_image := media_item.thumbnail:
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
