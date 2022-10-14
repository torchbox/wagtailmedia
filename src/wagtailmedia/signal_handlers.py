from django.db import transaction
from django.db.models.signals import post_delete

from wagtailmedia.models import get_media_model


def delete_files(instance):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)
    if instance.thumbnail:
        instance.thumbnail.delete(False)


def post_delete_file_cleanup(instance, **kwargs):
    transaction.on_commit(lambda: delete_files(instance))


def register_signal_handlers():
    Media = get_media_model()
    post_delete.connect(post_delete_file_cleanup, sender=Media)
