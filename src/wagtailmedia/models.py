import mimetypes
import os.path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.dispatch import Signal
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager
from wagtail.models import CollectionMember, ReferenceIndex
from wagtail.search import index
from wagtail.search.queryset import SearchableQuerySetMixin

from wagtailmedia.settings import wagtailmedia_settings


ALLOWED_EXTENSIONS_THUMBNAIL = ["gif", "jpg", "jpeg", "png", "webp"]


class MediaType(models.TextChoices):
    AUDIO = "audio", _("Audio file")
    VIDEO = "video", _("Video file")


class MediaQuerySet(SearchableQuerySetMixin, models.QuerySet):
    pass


class AbstractMedia(CollectionMember, index.Indexed, models.Model):
    title = models.CharField(max_length=255, verbose_name=_("title"))
    file = models.FileField(upload_to="media", verbose_name=_("file"))

    type = models.CharField(
        choices=MediaType.choices, max_length=255, blank=False, null=False
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
        index.SearchField("title", boost=10),
        index.AutocompleteField("title", boost=10),
        index.FilterField("title"),
        index.RelatedFields(
            "tags",
            [
                index.SearchField("name", boost=10),
                index.AutocompleteField("name", boost=10),
            ],
        ),
        index.FilterField("uploaded_by_user"),
        index.FilterField("type"),
    ]

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

    def __str__(self):
        return self.title

    @property
    def icon(self):
        return f"wagtailmedia-{self.type}"

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    @property
    def thumbnail_filename(self) -> str:
        return os.path.basename(self.thumbnail.name) if self.thumbnail else ""

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
        return ReferenceIndex.get_references_to(self).group_by_source_object()

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

        if self.thumbnail:
            validate = FileExtensionValidator(ALLOWED_EXTENSIONS_THUMBNAIL)
            validate(self.thumbnail)

        if self.type == "audio" and wagtailmedia_settings.AUDIO_EXTENSIONS:
            validate = FileExtensionValidator(wagtailmedia_settings.AUDIO_EXTENSIONS)
            validate(self.file)
        elif self.type == "video" and wagtailmedia_settings.VIDEO_EXTENSIONS:
            validate = FileExtensionValidator(wagtailmedia_settings.VIDEO_EXTENSIONS)
            validate(self.file)

    class Meta:
        abstract = True
        verbose_name = _("media")
        verbose_name_plural = _("media items")


class Media(AbstractMedia):
    pass


def get_media_model():
    from django.apps import apps

    from wagtailmedia.settings import wagtailmedia_settings

    try:
        app_label, model_name = wagtailmedia_settings.MEDIA_MODEL.split(".")
    except AttributeError:
        return Media
    except ValueError as err:
        raise ImproperlyConfigured(
            "WAGTAILMEDIA[\"MEDIA_MODEL\"] must be of the form 'app_label.model_name'"
        ) from err

    media_model = apps.get_model(app_label, model_name)
    if media_model is None:
        raise ImproperlyConfigured(
            f"WAGTAILMEDIA[\"MEDIA_MODEL\"] refers to model '{wagtailmedia_settings.MEDIA_MODEL}' that has not been installed"
        )

    return media_model


# Provides `request` as an argument
media_served = Signal()
