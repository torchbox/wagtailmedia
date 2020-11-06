from django.urls import path, re_path

from wagtailmedia.views import chooser, media


urlpatterns = [
    path("", media.index, name="index"),
    re_path(r"^(?P<media_type>audio|video|media)/add/$", media.add, name="add"),
    path("edit/<int:media_id>/", media.edit, name="edit"),
    path("delete/<int:media_id>/", media.delete, name="delete"),
    path("chooser/", chooser.chooser, name="chooser"),
    path("chooser/<int:media_id>/", chooser.media_chosen, name="media_chosen"),
    re_path(
        r"^(?P<media_type>audio|video)/chooser/upload/$",
        chooser.chooser_upload,
        name="chooser_upload",
    ),
    path("usage/<int:media_id>/", media.usage, name="media_usage"),
]
