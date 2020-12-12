import os
import subprocess

from django.conf import settings
from django.core.files import File

from wagtail import VERSION as WAGTAIL_VERSION


if WAGTAIL_VERSION < (2, 5):
    from wagtail.utils.pagination import paginate
else:
    from django.core.paginator import Paginator

    DEFAULT_PAGE_KEY = "p"

    def paginate(request, items, page_key=DEFAULT_PAGE_KEY, per_page=20):
        paginator = Paginator(items, per_page)
        page = paginator.get_page(request.GET.get(page_key))
        return paginator, page


def convert_gif(media):
    # 1) save the FieldFile data as a temp file for ffmpeg
    tmp_src_path = os.path.join(settings.WAGTAILMEDIA_TMP_DIRECTORY, media.filename)
    with open(tmp_src_path, 'wb+') as tmp_src_file:
        for chunk in media.file.chunks():
            tmp_src_file.write(chunk)

    # 2) run ffmpeg to convert the .gif into an .mp4 temp video file
    mp4_name = os.path.splitext(media.filename)[0] + '.mp4'
    tmp_dest_path = os.path.join(settings.WAGTAILMEDIA_TMP_DIRECTORY, mp4_name)
    process = ['ffmpeg', '-y', '-i', tmp_src_path, '-b:v', '500k', '-crf', '25', '-f', 'mp4', '-vcodec',
               'libx264', '-pix_fmt', 'yuv420p', '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2', tmp_dest_path]
    subprocess.run(process)

    # 3) save a copy of the temp video file in the correct django storage location
    #    by associating it with the model
    media.file = File(open(tmp_dest_path, 'rb'))
    media.file.name = mp4_name

    # 4) delete temp files
    os.unlink(tmp_src_path)
    os.unlink(tmp_dest_path)
