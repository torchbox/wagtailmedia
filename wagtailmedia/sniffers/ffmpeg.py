from __future__ import unicode_literals

import json
import subprocess
import sys
import os

from django.conf import settings


def sniff_media_data(video_path):
    ''' Uses ffprobe to sniff mediainfo metadata. '''
    ffprobe = settings.WAGTAILMEDIA_FFPROBE_CMD
    p = subprocess.check_output([ffprobe, "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams",
                                 video_path])
    return json.loads(p.decode(sys.stdout.encoding))


def generate_media_thumb(video_path, out_path, skip_seconds=0):
    ''' Uses ffmpeg to scrape out a thumbnail image from a video file. '''
    ffmpeg = settings.WAGTAILMEDIA_FFMPEG_CMD
    subprocess.check_output([ffmpeg, "-y", "-v", "quiet", "-accurate_seek", "-ss", str(skip_seconds), "-i", video_path,
                             "-frames:v", "1", out_path])
    return out_path

def get_stream_by_type(data, typestr):
    ''' Returns the appropriate mediainfo stream data. '''
    for stream in data['streams']:
        if stream['codec_type'] == typestr:
            return stream
    return None


def get_video_stream_data(data):
    ''' Returns the video mediainfo stream data. '''
    return get_stream_by_type(data, 'video')


def get_audio_stream_data(data):
    ''' Returns the audio mediainfo stream data. '''
    return get_stream_by_type(data, 'audio')
