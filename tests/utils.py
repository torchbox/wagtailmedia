import re

from typing import Optional

from django.core.files.base import ContentFile

from wagtailmedia.models import MediaType, get_media_model


Media = get_media_model()


def create_media(
    media_type: str,
    title: str,
    duration: Optional[int] = 100,
    thumbnail: Optional[str] = False,
) -> Media:
    filename = re.sub(r"[/:\"\'] ", "_", title).lower()
    extension = "mp3" if media_type == MediaType.AUDIO else "mp4"
    item = Media.objects.create(
        type=media_type,
        title=title,
        duration=duration,
        file=ContentFile("📼", name=f"{filename}.{extension}"),
    )

    if thumbnail:
        item.thumbnail = ContentFile("Thumbnail", name=thumbnail)
        item.save()

    return item


def create_video(title="Test video", duration=100, thumbnail=None) -> Media:
    return create_media(
        MediaType.VIDEO, title=title, duration=duration, thumbnail=thumbnail
    )


def create_audio(title="Test audio", duration=100, thumbnail=None) -> Media:
    return create_media(
        MediaType.AUDIO, title=title, duration=duration, thumbnail=thumbnail
    )
