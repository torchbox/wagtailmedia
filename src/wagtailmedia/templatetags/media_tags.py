from django.template import Library
from wagtail import VERSION as WAGTAIL_VERSION


register = Library()


@register.simple_tag
def wagtail_version(*version):
    return WAGTAIL_VERSION >= version
