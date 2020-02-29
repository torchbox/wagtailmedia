from draftjs_exporter.dom import DOM
from wagtail.admin.rich_text.converters.contentstate_models import Entity
from wagtail.admin.rich_text.converters.html_to_contentstate import AtomicBlockEntityElementHandler

from wagtailmedia.models import get_media_model


def media_entity(props):
    """
    Helper to construct elements of the form
    <embed embedtype="custommedia" id="1"/>
    when converting from contentstate data
    """
    return DOM.create_element('embed', {
        'embedtype': 'wagtailmedia',
        'id': props.get('id'),
        'title': props.get('title'),
        'type': props.get('type'),

        'thumbnail': props.get('thumbnail'),
        'file': props.get('file'),

        'autoplay': props.get('autoplay'),
        'mute': props.get('mute'),
        'loop': props.get('loop'),
    })


class MediaElementHandler(AtomicBlockEntityElementHandler):
    """
    Rule for building a media entity when converting from
    database representation to contentstate
    """
    def create_entity(self, name, attrs, state, contentstate):
        Media = get_media_model()
        try:
            media = Media.objects.get(id=attrs['id'])
        except Media.DoesNotExist:
            media = None

        return Entity('MEDIA', 'IMMUTABLE', {
            'id': attrs['id'],
            'title': media.title,
            'type': media.type,

            'thumbnail': media.thumbnail.url if media.thumbnail else '',
            'file': media.file.url if media.file else '',

            'autoplay': True if attrs.get('autoplay') == 'true' else False,
            'loop': True if attrs.get('loop') == 'true' else False,
            'mute': True if attrs.get('mute') == 'true' else False
        })


ContentstateMediaConversionRule = {
    'from_database_format': {
        'embed[embedtype="wagtailmedia"]': MediaElementHandler(),
    },
    'to_database_format': {
        'entity_decorators': {
            'MEDIA': media_entity
        }
    }
}
