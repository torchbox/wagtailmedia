import rest_framework.fields

from rest_framework.fields import ReadOnlyField
from wagtail.api.v2.serializers import BaseSerializer


class MediaDownloadUrlField(ReadOnlyField):
    """
    Serializes the "download_url" field for media items.

    Example:
    "download_url": "/media/my_video.mp4"
    """

    def get_attribute(self, instance):
        return instance

    def to_representation(self, media):
        return media.url


class MediaItemSerializer(BaseSerializer):
    download_url = MediaDownloadUrlField()
    media_type = rest_framework.fields.CharField(source="type")
