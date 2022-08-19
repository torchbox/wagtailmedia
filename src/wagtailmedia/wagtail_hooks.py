from django.conf.urls import include
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from wagtail import VERSION as WAGTAIL_VERSION
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
    if WAGTAIL_VERSION >= (4, 0, 0):
        return MediaMenuItem(
            _("Media"),
            reverse("wagtailmedia:index"),
            name="media",
            icon_name="media",
            order=300,
        )
    else:
        return MediaMenuItem(
            _("Media"),
            reverse("wagtailmedia:index"),
            name="media",
            classnames="icon icon-media",
            order=300,
        )


class MediaSummaryItem(SummaryItem):
    order = 300
    if WAGTAIL_VERSION >= (4, 0, 0):
        template_name = "wagtailmedia/homepage/site_summary_media.html"
    else:
        template_name = "wagtailmedia/homepage/legacy_site_summary_media.html"

    def get_context_data(self, parent_context):
        context = super().get_context_data(parent_context)
        context["total_media"] = get_media_model().objects.count()
        return context

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
            "count_text": ngettext(
                "%(count)s media file", "%(count)s media files", media_count
            )
            % {"count": media_count},
            "url": url,
        }
