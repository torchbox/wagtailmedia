from django.conf import settings
from django.conf.urls import include
from django.urls import path
from django.views.static import serve

from wagtail import VERSION as WAGTAIL_VERSION
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.api.v2.router import WagtailAPIRouter


if WAGTAIL_VERSION >= (3, 0):
    from wagtail import urls as wagtail_urls
else:
    from wagtail.core import urls as wagtail_urls

from wagtail.documents import urls as wagtaildocs_urls

from wagtailmedia.api.views import MediaAPIViewSet


api_router = WagtailAPIRouter("wagtailapi_v2")
api_router.register_endpoint("media", MediaAPIViewSet)

urlpatterns = [
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("api/", api_router.urls),
    path("", include(wagtail_urls)),
] + [
    path(
        "%s<path:path>" % prefix.lstrip("/"),
        serve,
        kwargs={"document_root": document_root},
    )
    for prefix, document_root in (
        (settings.STATIC_URL, settings.STATIC_ROOT),
        (settings.MEDIA_URL, settings.MEDIA_ROOT),
    )
]
