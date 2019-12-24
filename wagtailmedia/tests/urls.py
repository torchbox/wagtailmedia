import re

from django.conf import settings
from django.conf.urls import include, url
from django.views.static import serve

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls

urlpatterns = [
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'', include(wagtail_urls)),
] + [
    url(r'^%s(?P<path>.*)$' % re.escape(prefix.lstrip('/')), serve, kwargs={'document_root': document_root})
    for prefix, document_root in (
        (settings.STATIC_URL, settings.STATIC_ROOT),
        (settings.MEDIA_URL, settings.MEDIA_ROOT),
    )
]
