from __future__ import unicode_literals

import mimetypes
import os.path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.validators import MinValueValidator
from django.db import models
from django.dispatch import Signal
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from wagtail import VERSION as WAGTAIL_VERSION
from wagtail.core.models import CollectionMember
from wagtail.search import index
from wagtail.search.queryset import SearchableQuerySetMixin

from taggit.managers import TaggableManager


if WAGTAIL_VERSION < (2, 9):
    from wagtail.admin.utils import get_object_usage
else:
    from wagtail.admin.models import get_object_usage


class MediaQuerySet(SearchableQuerySetMixin, models.QuerySet):
    pass


class AbstractMedia(CollectionMember, index.Indexed, models.Model):
    MEDIA_TYPES = (
        ("audio", _("Audio file")),
        ("video", _("Video file")),
    )

    title = models.CharField(max_length=255, verbose_name=_("title"))
    file = models.FileField(upload_to="media", verbose_name=_("file"))

    type = models.CharField(
        choices=MEDIA_TYPES, max_length=255, blank=False, null=False
    )
    duration = models.FloatField(
        blank=True,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("duration"),
        help_text=_("Duration in seconds"),
    )
    width = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("width"))
    height = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_("height")
    )
    thumbnail = models.FileField(
        upload_to="media_thumbnails", blank=True, verbose_name=_("thumbnail")
    )

    created_at = models.DateTimeField(verbose_name=_("created at"), auto_now_add=True)
    uploaded_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("uploaded by user"),
        null=True,
        blank=True,
        editable=False,
        on_delete=models.SET_NULL,
    )

    tags = TaggableManager(help_text=None, blank=True, verbose_name=_("tags"))

    objects = MediaQuerySet.as_manager()

    search_fields = CollectionMember.search_fields + [
        index.SearchField("title", partial_match=True, boost=10),
        index.RelatedFields(
            "tags",
            [
                index.SearchField("name", partial_match=True, boost=10),
            ],
        ),
        index.FilterField("uploaded_by_user"),
    ]

    def __str__(self):
        return self.title

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    @property
    def thumbnail_filename(self):
        return os.path.basename(self.thumbnail.name)

    @property
    def file_extension(self):
        return os.path.splitext(self.filename)[1][1:]

    @property
    def url(self):
        return self.file.url

    @property
    def sources(self):
        return [
            {
                "src": self.url,
                "type": mimetypes.guess_type(self.filename)[0]
                or "application/octet-stream",
            }
        ]

    def get_usage(self):
        return get_object_usage(self)

    @property
    def usage_url(self):
        return reverse("wagtailmedia:media_usage", args=(self.id,))

    def is_editable_by_user(self, user):
        from wagtailmedia.permissions import permission_policy

        return permission_policy.user_has_permission_for_instance(user, "change", self)

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        if not self.duration:
            self.duration = 0

    class Meta:
        abstract = True
        verbose_name = _("media")


class Media(AbstractMedia):
    admin_form_fields = (
        "title",
        "file",
        "collection",
        "duration",
        "width",
        "height",
        "thumbnail",
        "tags",
    )


def get_media_model():
    from django.apps import apps
    from django.conf import settings

    try:
        app_label, model_name = settings.WAGTAILMEDIA_MEDIA_MODEL.split(".")
    except AttributeError:
        return Media
    except ValueError:
        raise ImproperlyConfigured(
            "WAGTAILMEDIA_MEDIA_MODEL must be of the form 'app_label.model_name'"
        )

    media_model = apps.get_model(app_label, model_name)
    if media_model is None:
        raise ImproperlyConfigured(
            "WAGTAILMEDIA_MEDIA_MODEL refers to model '%s' that has not been installed"
            % settings.WAGTAILMEDIA_MEDIA_MODEL
        )
    return media_model


# Provides `request` as an argument
media_served = Signal()
