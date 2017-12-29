from __future__ import unicode_literals

import os.path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files import File
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import Signal
from django.dispatch.dispatcher import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from taggit.managers import TaggableManager
from wagtail.wagtailadmin.utils import get_object_usage
from wagtail.wagtailcore.models import CollectionMember
from wagtail.wagtailsearch import index
from wagtail.wagtailsearch.queryset import SearchableQuerySetMixin

from .sniffers.ffmpeg import (
    generate_media_thumb, get_video_stream_data, sniff_media_data
)


class MediaQuerySet(SearchableQuerySetMixin, models.QuerySet):
    pass


@python_2_unicode_compatible
class AbstractMedia(CollectionMember, index.Indexed, models.Model):
    MEDIA_TYPES = (
        ('audio', _('Audio file')),
        ('video', _('Video file')),
    )

    title = models.CharField(max_length=255, verbose_name=_('title'))
    file = models.FileField(upload_to='media', verbose_name=_('file'))

    type = models.CharField(choices=MEDIA_TYPES, max_length=255, blank=False, null=False)
    duration = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('duration'),
                                           help_text=_('Duration in seconds'))
    width = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('width'))
    height = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('height'))
    thumbnail = models.FileField(upload_to='media_thumbnails', blank=True, verbose_name=_('thumbnail'))

    mediainfo = models.TextField(null=True, blank=True, verbose_name=_('mediainfo'))

    created_at = models.DateTimeField(verbose_name=_('created at'), auto_now_add=True)
    uploaded_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('uploaded by user'),
        null=True,
        blank=True,
        editable=False,
        on_delete=models.SET_NULL
    )

    tags = TaggableManager(help_text=None, blank=True, verbose_name=_('tags'))

    objects = MediaQuerySet.as_manager()

    search_fields = CollectionMember.search_fields + [
        index.SearchField('title', partial_match=True, boost=10),
        index.RelatedFields('tags', [
            index.SearchField('name', partial_match=True, boost=10),
        ]),
        index.FilterField('uploaded_by_user'),
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

    def get_usage(self):
        return get_object_usage(self)

    @property
    def usage_url(self):
        return reverse('wagtailmedia:media_usage',
                       args=(self.id,))

    def is_editable_by_user(self, user):
        from wagtailmedia.permissions import permission_policy
        return permission_policy.user_has_permission_for_instance(user, 'change', self)

    def save(self, *args, **kwargs):
        ''' Send changed field names through to signals. '''
        if self.pk is not None:
            old = self.__class__._default_manager.filter(pk=self.pk).values()[0]
            changed = []
            for field in old.keys():
                if getattr(self, field) != old[field]:
                    changed.append(field)
            if changed:
                kwargs['update_fields'] = changed
        super(AbstractMedia, self).save(*args, **kwargs)

    class Meta:
        abstract = True
        verbose_name = _('media')


class Media(AbstractMedia):
    admin_form_fields = (
        'title',
        'file',
        'collection',
        'duration',
        'width',
        'height',
        'thumbnail',
        'tags',
    )


def get_media_model():
    from django.conf import settings
    from django.apps import apps

    try:
        app_label, model_name = settings.WAGTAILMEDIA_MEDIA_MODEL.split('.')
    except AttributeError:
        return Media
    except ValueError:
        raise ImproperlyConfigured("WAGTAILMEDIA_MEDIA_MODEL must be of the form 'app_label.model_name'")

    media_model = apps.get_model(app_label, model_name)
    if media_model is None:
        raise ImproperlyConfigured(
            "WAGTAILMEDIA_MEDIA_MODEL refers to model '%s' that has not been installed" %
            settings.WAGTAILMEDIA_MEDIA_MODEL
        )
    return media_model


# Receive the post_save signal and sniff mediainfo data if possible.
@receiver(post_save, sender=Media)
def media_sniff(sender, instance, created, update_fields, **kwargs):
    if hasattr(settings, 'WAGTAILMEDIA_FFPROBE_CMD'):
        if created or (update_fields and 'file' in update_fields):
            data = sniff_media_data(instance.file.path)
            if data:
                duration = int(float(data['format']['duration']))
                Media.objects.filter(pk=instance.pk).update(duration=duration, mediainfo=data)
                if instance.type == 'video':
                    video_stream = get_video_stream_data(data)
                    if video_stream:
                        height = int(float(video_stream['height']))
                        width = int(float(video_stream['width']))
                        Media.objects.filter(pk=instance.pk).update(height=height, width=width)

                    # Try to scrape a thumbnail from video
                    if hasattr(settings, 'WAGTAILMEDIA_FFMPEG_CMD')\
                            and not instance.thumbnail:
                        thumb_path = generate_media_thumb(instance.file.path, f'{instance.file.name}.jpg',
                                                          skip_seconds=int(duration*1.0/2))
                        instance.thumbnail.save(os.path.basename(thumb_path), File(open(thumb_path, 'rb')))
                        os.remove(thumb_path)


# Receive the pre_delete signal and delete the file associated with the model instance.
@receiver(pre_delete, sender=Media)
def media_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)
    instance.thumbnail.delete(False)


media_served = Signal(providing_args=['request'])
