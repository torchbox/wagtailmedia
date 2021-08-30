from django.conf import settings
from django.conf.urls import include
from django.urls import path
from django.views.static import serve

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls


urlpatterns = [
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
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
