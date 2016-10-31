from django.db import models

from modelcluster.fields import ParentalKey
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Orderable, Page
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel


class EventPageRelatedMedia(Orderable):
    page = ParentalKey('wagtailmedia_tests.EventPage', related_name='related_media')
    title = models.CharField(max_length=255, help_text="Link title")
    link_media = models.ForeignKey(
        'wagtailmedia.Media',
        null=True,
        blank=True,
        related_name='+'
    )

    @property
    def link(self):
        return self.link_media.url

    panels = [
        FieldPanel('title'),
        DocumentChooserPanel('link_media'),
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
