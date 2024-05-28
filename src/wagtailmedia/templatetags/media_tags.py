from django.template import Library
from wagtail.utils.version import get_main_version


register = Library()


@register.simple_tag
def wagtail_version_gte(version: str) -> bool:
    return get_main_version() >= version
