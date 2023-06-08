import rest_framework.fields

from rest_framework.fields import ReadOnlyField
from wagtail.api.v2.serializers import BaseSerializer
from wagtail.api.v2.utils import get_full_url


class MediaDownloadUrlField(ReadOnlyField):
    """
    Serializes the "download_url" field for media items.

    Example:
    "download_url": "http://api.example.com/media/my_video.mp4"
    """

    def get_attribute(self, instance):
        return instance

    def to_representation(self, instance):
        return get_full_url(self.context["request"], instance.url)


class MediaItemSerializer(BaseSerializer):
    download_url = MediaDownloadUrlField()
    media_type = rest_framework.fields.CharField(source="type")
