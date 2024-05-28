from django.template import Library
from wagtail import VERSION as WAGTAIL_VERSION


register = Library()


@register.simple_tag
def is_wagtail_version_gte(*version):
    return WAGTAIL_VERSION >= version
