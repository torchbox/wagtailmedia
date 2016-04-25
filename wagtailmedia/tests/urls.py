from django.conf.urls import include, url

from wagtail.wagtailcore import urls as wagtail_urls
from wagtail.wagtailadmin import urls as wagtailadmin_urls

urlpatterns = [
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'', include(wagtail_urls)),
]
