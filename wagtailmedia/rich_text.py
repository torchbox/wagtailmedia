from django.utils.html import escape

from wagtailmedia.models import get_media_model


class MediaLinkHandler(object):
    @staticmethod
    def get_db_attributes(tag):
        return {'id': tag['data-id']}

    @staticmethod
    def expand_db_attributes(attrs, for_editor):
        Media = get_media_model()
        try:
            media = Media.objects.get(id=attrs['id'])

            if for_editor:
                editor_attrs = 'data-linktype="media" data-id="%d" ' % media.id
            else:
                editor_attrs = ''

            return '<a %shref="%s">' % (editor_attrs, escape(media.url))
        except Media.DoesNotExist:
            return "<a>"
