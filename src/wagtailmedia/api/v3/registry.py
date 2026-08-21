from wagtail.api.v3.registry import ContentTypeRegistration, registry

from wagtailmedia import get_media_model

from .schemas import build_media_schemas


def register_content_types() -> None:
    Media = get_media_model()
    read_schema, create_schema, patch_schema = build_media_schemas()
    registry.register(
        ContentTypeRegistration(
            name=Media._meta.label,
            label=str(Media._meta.verbose_name),
            read_schema=read_schema,
            create_schema=create_schema,
            patch_schema=patch_schema,
        )
    )
