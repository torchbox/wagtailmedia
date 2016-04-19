from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import StreamingHttpResponse, BadHeaderError

from unidecode import unidecode
from wsgiref.util import FileWrapper

from wagtail.utils.sendfile import sendfile
from wagtail.utils import sendfile_streaming_backend

from wagtailmedia.models import get_media_model, media_served


def serve(request, media_id, media_filename):
    media_model = get_media_model()
    media = get_object_or_404(media_model, id=media_id)

    # Send media_served signal
    media_served.send(sender=media_model, instance=media, request=request)

    try:
        local_path = media.file.path
    except NotImplementedError:
        local_path = None

    if local_path:

        # Use wagtail.utils.sendfile to serve the file;
        # this provides support for mimetypes, if-modified-since and django-sendfile backends

        if hasattr(settings, 'SENDFILE_BACKEND'):
            return sendfile(request, local_path, attachment=True, attachment_filename=media.filename)
        else:
            # Fallback to streaming backend if user hasn't specified SENDFILE_BACKEND
            return sendfile(
                request,
                local_path,
                attachment=True,
                attachment_filename=media.filename,
                backend=sendfile_streaming_backend.sendfile
            )

    else:

        # We are using a storage backend which does not expose filesystem paths
        # (e.g. storages.backends.s3boto.S3BotoStorage).
        # Fall back on pre-sendfile behaviour of reading the file content and serving it
        # as a StreamingHttpResponse

        wrapper = FileWrapper(media.file)
        response = StreamingHttpResponse(wrapper, content_type='application/octet-stream')

        try:
            response['Content-Disposition'] = 'attachment; filename=%s' % media.filename
        except BadHeaderError:
            # Unicode filenames can fail on Django <1.8, Python 2 due to
            # https://code.djangoproject.com/ticket/20889 - try with an ASCIIfied version of the name
            response['Content-Disposition'] = 'attachment; filename=%s' % unidecode(media.filename)

        # FIXME: storage backends are not guaranteed to implement 'size'
        response['Content-Length'] = media.file.size

        return response
