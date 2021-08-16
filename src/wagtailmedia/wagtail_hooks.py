from django.conf.urls import include
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ungettext

from wagtail.admin.menu import MenuItem
from wagtail.admin.search import SearchArea
from wagtail.admin.site_summary import SummaryItem
from wagtail.core import hooks

from wagtailmedia import admin_urls
from wagtailmedia.forms import GroupMediaPermissionFormSet
from wagtailmedia.models import get_media_model
from wagtailmedia.permissions import permission_policy


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [
        path("media/", include((admin_urls, "wagtailmedia"), namespace="wagtailmedia")),
    ]


class MediaMenuItem(MenuItem):
    def is_shown(self, request):
        return permission_policy.user_has_any_permission(
            request.user, ["add", "change", "delete"]
        )


@hooks.register("register_admin_menu_item")
def register_media_menu_item():
    return MediaMenuItem(
        _("Media"),
        reverse("wagtailmedia:index"),
        name="media",
        classnames="icon icon-media",
        order=300,
    )


@hooks.register("insert_editor_js")
def editor_js():
    return format_html(
        """
        <script>
            window.chooserUrls.mediaChooser = '{0}';
        </script>
        """,
        reverse("wagtailmedia:chooser"),
    )


class MediaSummaryItem(SummaryItem):
    order = 300
    template = "wagtailmedia/homepage/site_summary_media.html"

    def get_context(self):
        return {
            "total_media": get_media_model().objects.count(),
        }

    def is_shown(self):
        return permission_policy.user_has_any_permission(
            self.request.user, ["add", "change", "delete"]
        )


@hooks.register("construct_homepage_summary_items")
def add_media_summary_item(request, items):
    items.append(MediaSummaryItem(request))


class MediaSearchArea(SearchArea):
    def is_shown(self, request):
        return permission_policy.user_has_any_permission(
            request.user, ["add", "change", "delete"]
        )


@hooks.register("register_admin_search_area")
def register_media_search_area():
    return MediaSearchArea(
        _("Media"),
        reverse("wagtailmedia:index"),
        name="media",
        classnames="icon icon-media",
        order=400,
    )


@hooks.register("register_group_permission_panel")
def register_media_permissions_panel():
    return GroupMediaPermissionFormSet


@hooks.register("describe_collection_contents")
def describe_collection_media(collection):
    media_count = get_media_model().objects.filter(collection=collection).count()
    if media_count:
        url = reverse("wagtailmedia:index") + ("?collection_id=%d" % collection.id)
        return {
            "count": media_count,
            "count_text": ungettext(
                "%(count)s media file", "%(count)s media files", media_count
            )
            % {"count": media_count},
            "url": url,
        }
