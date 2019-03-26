import json

from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _

from wagtailmedia.models import get_media_model
from wagtailmedia.permissions import permission_policy

try:
    from django.urls import reverse
except ImportError:  # fallback for older Django
    from django.core.urlresolvers import reverse

try:
    from wagtail.utils.pagination import paginate
    from wagtail.admin.forms import SearchForm
    from wagtail.admin.modal_workflow import render_modal_workflow
    from wagtail.admin.utils import PermissionPolicyChecker
    from wagtail.core.models import Collection
except ImportError:  # fallback for wagtail <2.0
    from wagtail.utils.pagination import paginate
    from wagtail.wagtailadmin.forms import SearchForm
    from wagtail.wagtailadmin.modal_workflow import render_modal_workflow
    from wagtail.wagtailadmin.utils import PermissionPolicyChecker
    from wagtail.wagtailcore.models import Collection


permission_checker = PermissionPolicyChecker(permission_policy)


def get_chooser_json():
    """construct context variables needed by the chooser JS"""
    return {
        'step': 'chooser',
        'error_label': _("Server Error"),
        'error_message': _("Report this error to your webmaster with the following information:"),
	'tag_autocomplete_url': reverse('wagtailadmin_tag_autocomplete'),
    }

def chooser(request):
    Media = get_media_model()

    media_files = []

    q = None
    is_searching = False
    if 'q' in request.GET or 'p' in request.GET or 'collection_id' in request.GET:
        media_files = Media.objects.all()

        collection_id = request.GET.get('collection_id')
        if collection_id:
            media_files = media_files.filter(collection=collection_id)

        searchform = SearchForm(request.GET)
        if searchform.is_valid():
            q = searchform.cleaned_data['q']

            media_files = media_files.search(q)
            is_searching = True
        else:
            media_files = media_files.order_by('-created_at')
            is_searching = False

        # Pagination
        paginator, media_files = paginate(request, media_files, per_page=10)

        return render(request, "wagtailmedia/chooser/results.html", {
            'media_files': media_files,
            'query_string': q,
            'is_searching': is_searching,
        })
    else:
        searchform = SearchForm()

        collections = Collection.objects.all()
        if len(collections) < 2:
            collections = None

        media_files = Media.objects.order_by('-created_at')
        paginator, media_files = paginate(request, media_files, per_page=10)

    context =  {
        'media_files': media_files,
        'searchform': searchform,
        'collections': collections,
        'is_searching': False,
    }

    return render_modal_workflow(
        request, 'wagtailmedia/chooser/chooser.html', None, context, get_chooser_json()
    )

def get_media_json(media):
    """
    helper function: given a media, return the json to pass back to the
    chooser panel
    """
    return {
        'id': media.id,
        'title': media.title,
        'edit_link': reverse('wagtailmedia:edit', args=(media.id,)),
    }

def media_chosen(request, media_id):
    media = get_object_or_404(get_media_model(), id=media_id)

    return render_modal_workflow(
        request, None, None, None,
        {'step': 'media_chosen', 'result': get_media_json(media)}
    )
