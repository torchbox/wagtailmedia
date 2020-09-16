from django.db import models

from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Orderable, Page

from wagtailmedia.edit_handlers import MediaChooserPanel
from wagtailmedia.models import AbstractMedia


class CustomMedia(AbstractMedia):
    pass


class EventPageRelatedMedia(Orderable):
    page = ParentalKey('wagtailmedia_tests.EventPage', related_name='related_media', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, help_text="Link title")
    link_media = models.ForeignKey(
        'wagtailmedia.Media',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.CASCADE
    )

    @property
    def link(self):
        return self.link_media.url

    panels = [
        FieldPanel('title'),
        MediaChooserPanel('link_media'),
    ]


class EventPage(Page):
    date_from = models.DateField("Start date", null=True)
    date_to = models.DateField(
        "End date",
        null=True,
        blank=True,
        help_text="Not required if event is on a single day"
    )
    time_from = models.TimeField("Start time", null=True, blank=True)
    time_to = models.TimeField("End time", null=True, blank=True)
    location = models.CharField(max_length=255)
    body = RichTextField(blank=True)
    cost = models.CharField(max_length=255)
    signup_link = models.URLField(blank=True)


EventPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('date_from'),
    FieldPanel('date_to'),
    FieldPanel('time_from'),
    FieldPanel('time_to'),
    FieldPanel('location'),
    FieldPanel('cost'),
    FieldPanel('signup_link'),
    FieldPanel('body', classname="full"),
    InlinePanel('related_media', label="Related media"),
]
