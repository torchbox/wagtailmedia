from django.db import models
from django.forms.utils import flatatt
from django.utils.html import format_html, format_html_join

from modelcluster.fields import ParentalKey
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page

from wagtailmedia.blocks import (
    AbstractMediaChooserBlock,
    AudioChooserBlock,
    VideoChooserBlock,
)
from wagtailmedia.edit_handlers import MediaChooserPanel
from wagtailmedia.models import AbstractMedia, Media


class CustomMedia(AbstractMedia):
    fancy_caption = RichTextField(blank=True)

    admin_form_fields = Media.admin_form_fields + ("fancy_caption",)


class EventPageRelatedMedia(Orderable):
    page = ParentalKey(
        "wagtailmedia_tests.EventPage",
        related_name="related_media",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255, help_text="Link title")
    link_media = models.ForeignKey(
        "wagtailmedia.Media",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.CASCADE,
    )

    @property
    def link(self):
        return self.link_media.url

    panels = [
        FieldPanel("title"),
        MediaChooserPanel("link_media"),
    ]


class EventPage(Page):
    date_from = models.DateField("Start date", null=True)
    date_to = models.DateField(
        "End date",
        null=True,
        blank=True,
        help_text="Not required if event is on a single day",
    )
    time_from = models.TimeField("Start time", null=True, blank=True)
    time_to = models.TimeField("End time", null=True, blank=True)
    location = models.CharField(max_length=255)
    body = RichTextField(blank=True)
    cost = models.CharField(max_length=255)
    signup_link = models.URLField(blank=True)


EventPage.content_panels = Page.content_panels + [
    FieldPanel("date_from"),
    FieldPanel("date_to"),
    FieldPanel("time_from"),
    FieldPanel("time_to"),
    FieldPanel("location"),
    FieldPanel("cost"),
    FieldPanel("signup_link"),
    FieldPanel("body"),
    InlinePanel("related_media", heading="Related media", label="Media item"),
]


class TestMediaBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        if not value:
            return ""

        if value.type == "video":
            player_code = """
            <div>
                <video width="320" height="240" controls>
                    {0}
                    Your browser does not support the video tag.
                </video>
            </div>
            """
        else:
            player_code = """
            <div>
                <audio controls>
                    {0}
                    Your browser does not support the audio element.
                </audio>
            </div>
            """

        return format_html(
            player_code,
            format_html_join(
                "\n", "<source{0}>", [[flatatt(s)] for s in value.sources]
            ),
        )


class BlogStreamPage(Page):
    author = models.CharField(max_length=255)
    date = models.DateField("Post date")

    body = StreamField(
        [
            ("heading", blocks.CharBlock(classname="title", icon="title")),
            ("paragraph", blocks.RichTextBlock(icon="pilcrow")),
            ("media", TestMediaBlock(icon="media")),
            ("video", VideoChooserBlock(icon="media")),
            ("audio", AudioChooserBlock(icon="media")),
        ],
        use_json_field=True,
    )

    featured_media = models.ForeignKey(
        "wagtailmedia.Media", on_delete=models.PROTECT, related_name="+"
    )

    content_panels = Page.content_panels + [
        FieldPanel("author"),
        FieldPanel("date"),
        FieldPanel("body"),
        MediaChooserPanel("featured_media"),
        # the following are left here for local testing convenience
        # MediaChooserPanel("featured_media", media_type="audio"),
        # MediaChooserPanel("featured_media", media_type="video"),
    ]
