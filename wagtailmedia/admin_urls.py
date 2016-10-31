from django.conf.urls import url

from wagtailmedia.views import chooser, media

urlpatterns = [
    url(r'^$', media.index, name='index'),
    url(r'^(\w+)/add/$', media.add, name='add'),
    url(r'^edit/(\d+)/$', media.edit, name='edit'),
    url(r'^delete/(\d+)/$', media.delete, name='delete'),

    url(r'^chooser/$', chooser.chooser, name='chooser'),
    url(r'^chooser/(\d+)/$', chooser.media_chosen, name='media_chosen'),
    url(r'^usage/(\d+)/$', media.usage, name='media_usage'),
]
