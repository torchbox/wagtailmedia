from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.paginator import Paginator
from django.forms.utils import flatatt
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext_lazy as _


if TYPE_CHECKING:
    from .models import AbstractMedia

DEFAULT_PAGE_KEY = "p"


def paginate(request, items, page_key=DEFAULT_PAGE_KEY, per_page=20):
    paginator = Paginator(items, per_page)
    page = paginator.get_page(request.GET.get(page_key))
    return paginator, page


def format_audio_html(item: AbstractMedia) -> str:
    return format_html(
        "<audio controls>\n{sources}\n<p>{fallback}</p>\n</audio>",
        sources=format_html_join(
            "\n", "<source{0}>", [[flatatt(s)] for s in item.sources]
        ),
        fallback=_("Your browser does not support the audio element."),
    )


def format_video_html(item: AbstractMedia) -> str:
    return format_html(
        "<video controls>\n{sources}\n<p>{fallback}</p>\n</video>",
        sources=format_html_join(
            "\n", "<source{0}>", [[flatatt(s)] for s in item.sources]
        ),
        fallback=_("Your browser does not support the video element."),
    )
