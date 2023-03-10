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


Media = get_media_model()


class MediaChooserMixin:
    def get_object_list(self):
        return Media.objects.select_related("collection").only(
            "title", "file", "type", "collection__name", "created_at"
        )

    @property
    def columns(self):
        return super().columns + [
            Column("file", label="File", accessor="file"),
            Column("type", label="Type", accessor="type"),
            Column("collection", label="Collection", accessor="collection"),
            Column("created_at", label="Uploaded", accessor="created_at"),
        ]


class MediaChooseView(MediaChooserMixin, ChooseView):
    pass


class MediaChooseResultsView(MediaChooserMixin, ChooseResultsView):
    pass


class MediaChosenView(ChosenView):
    def get_object(self, pk):
        return Media.objects.only("title", "thumbnail").get(pk=pk)


class MediaChooserViewSet(ChooserViewSet):
    choose_view_class = MediaChooseView
    chosen_view_class = MediaChosenView
    choose_results_view_class = MediaChooseResultsView
    creation_form_class = get_media_form(Media)

    icon = "media"
    choose_one_text = _("Choose a media item")
    choose_another_text = _("Choose another media item")
    edit_item_text = _("Edit this media item")
    creation_tab_label = _("Upload")
    create_action_label = _("Upload")
    create_action_clicked_label = _("Uploading…")
    form_fields = ["type", "title", "file", "collection", "thumbnail"]


media_chooser_viewset = MediaChooserViewSet("media_chooser", model=Media)
