from django.conf.urls import url
from wagtailmedia.views import serve

urlpatterns = [
    url(r'^(\d+)/(.*)$', serve.serve, name='wagtailmedia_serve'),
]
