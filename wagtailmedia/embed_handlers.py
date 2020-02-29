from django.template.loader import render_to_string

from wagtail import VERSION as WAGTAIL_VERSION

from wagtailmedia.models import get_media_model

if WAGTAIL_VERSION < (2, 5):
    from wagtail.embeds.rich_text import MediaEmbedHandler as EmbedHandler
else:
    from wagtail.core.rich_text import EmbedHandler


class MediaEmbedHandler(EmbedHandler):
    identifier = 'wagtailmedia'

    @staticmethod
    def get_model():
        return get_media_model()

    @staticmethod
    def expand_db_attributes(attrs):
        """
        Given a dict of attributes from the <embed> tag, return the real HTML
        representation for use on the front-end.
        """

        if(attrs['type'] == 'video'):
            template = 'wagtailmedia/embeds/video_embed.html'
        elif(attrs['type'] == 'audio'):
            template = 'wagtailmedia/embeds/audio_embed.html'

        return render_to_string(template, {
            'title': attrs['title'],

            'thumbnail': attrs['thumbnail'],
            'file': attrs['file'],

            'autoplay': True if attrs['autoplay'] == 'true' else False,
            'loop': True if attrs['loop'] == 'true' else False,
            'mute': True if attrs['mute'] == 'true' else False
        })
