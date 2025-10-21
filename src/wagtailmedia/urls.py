"""
URL patterns for wagtailmedia webhooks.

To enable webhooks in your project, include these URLs in your urlconf:

    from django.urls import path, include

    urlpatterns = [
        ...
        path('media/webhooks/', include('wagtailmedia.urls')),
        ...
    ]

This will make the webhook available at: /media/webhooks/transcoding/
"""

from django.urls import path

from wagtailmedia.settings import wagtailmedia_settings


app_name = "wagtailmedia"

urlpatterns = []

if wagtailmedia_settings.WEBHOOK_API_KEY:
    from wagtailmedia.views.webhooks import TranscodingWebhookView

    urlpatterns.append(
        path(
            "transcoding/",
            TranscodingWebhookView.as_view(),
            name="transcoding_webhook",
        ),
    )
