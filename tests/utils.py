import re
import shutil
import tempfile

from django.core.files.base import ContentFile
from django.test import TestCase

from wagtailmedia.models import AbstractMedia, MediaType, get_media_model


class TempDirMediaRootMixin(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def run(self, result=None):
        with self.settings(MEDIA_ROOT=self.tmpdir):
            return super().run(result)


def create_media(
    media_type: str,
    title: str,
    duration: int | None = 100,
    thumbnail: str | None = False,
    **kwargs,
) -> AbstractMedia:
    filename = re.sub(r"[/:\"\'] ", "_", title).lower()
    extension = "mp3" if media_type == MediaType.AUDIO else "mp4"

    defaults = {
        "type": media_type,
        "title": title,
        "duration": duration,
        "file": ContentFile("📼", name=f"{filename}.{extension}"),
    }
    defaults.update(kwargs)
    item = get_media_model().objects.create(**defaults)

    if thumbnail:
        item.thumbnail = ContentFile("Thumbnail", name=thumbnail)
        item.save(update_fields=["thumbnail"])

    return item


def create_video(
    title="Test video", duration=100, thumbnail=None, **kwargs
) -> AbstractMedia:
    return create_media(
        MediaType.VIDEO, title=title, duration=duration, thumbnail=thumbnail, **kwargs
    )


def create_audio(
    title="Test audio", duration=100, thumbnail=None, **kwargs
) -> AbstractMedia:
    return create_media(
        MediaType.AUDIO, title=title, duration=duration, thumbnail=thumbnail, **kwargs
    )
