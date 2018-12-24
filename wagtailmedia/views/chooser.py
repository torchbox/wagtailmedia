import json

from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _

from wagtailmedia.models import get_media_model
from wagtailmedia.permissions import permission_policy
from wagtailmedia.forms import get_media_form

try:
    from django.urls import reverse
except ImportError:  # fallback for older Django
    from django.core.urlresolvers import reverse

try:
    from wagtail.utils.pagination import paginate
    from wagtail.admin.forms.search import SearchForm
    from wagtail.admin.modal_workflow import render_modal_workflow
    from wagtail.admin.utils import PermissionPolicyChecker, popular_tags_for_model
    from wagtail.core.models import Collection
    from wagtail.core import hooks
    from wagtail.search import index as search_index
except ImportError:  # fallback for wagtail <2.0
    from wagtail.utils.pagination import paginate
    from wagtail.wagtailadmin.forms import SearchForm
    from wagtail.wagtailadmin.modal_workflow import render_modal_workflow
    from wagtail.wagtailadmin.utils import PermissionPolicyChecker
    from wagtail.wagtailcore.models import Collection


permission_checker = PermissionPolicyChecker(permission_policy)

def get_chooser_js_data():
    """construct context variables needed by the chooser JS"""
    return {
        'step': 'chooser',
        'error_label': _("Server Error"),
        'error_message': _("Report this error to your webmaster with the following information:"),
        'tag_autocomplete_url': reverse('wagtailadmin_tag_autocomplete'),
    }

def get_media_result_data(media):
    """
    helper function: given a media, return the json to pass back to the
    chooser panel
    """

    return {
        'id': media.id,
        'title': media.title,
        'edit_link': reverse('wagtailmedia:edit', args=(media.id,)),
    }

def get_chooser_context(request):
    """Helper function to return common template context variables for the main chooser view"""

    collections = Collection.objects.all()
    if len(collections) < 2:
        collections = None
    else:
        collections = Collection.order_for_display(collections)

    return {
        'searchform': SearchForm(),
        'is_searching': False,
        'query_string': None,
        'popular_tags': popular_tags_for_model(get_media_model()),
        'collections': collections,
}

def chooser(request):
    Media = get_media_model()

    if permission_policy.user_has_permission(request.user, 'add'):
        MediaForm = get_media_form(Media)
        uploadform = MediaForm(user=request.user)
    else:
        uploadform = None

    media_files = Media.objects.order_by('-created_at')

    #May not be necessary.
    for hook in hooks.get_hooks('construct_media_chooser_queryset'):
        media_files = hook(media_files, request)


    if (
        'q' in request.GET or 'p' in request.GET or 'collection_id' in request.GET):
        media_files = Media.objects.order_by('-created_at')

        collection_id = request.GET.get('collection_id')
        if collection_id:
            media_files = media_files.filter(collection=collection_id)

        searchform = SearchForm(request.GET)
        if searchform.is_valid():
            q = searchform.cleaned_data['q']

            media_files = media_files.search(q)
            is_searching = True
        else:
            is_searching = False
            q = None

        # Pagination
        paginator, media_files = paginate(request, media_files, per_page=10)

        return render(request, "wagtailmedia/chooser/results.html", {
            'media_files': media_files,
            'query_string': q,
            'is_searching': is_searching,
        })
    else:
        paginator, media_files = paginate(request, media_files, per_page=10)
        context = get_chooser_context(request)

        context.update({
            'media_files': media_files,
            'uploadform': uploadform,
        })

        return render_modal_workflow(request, 'wagtailmedia/chooser/chooser.html', None, context, json_data=get_chooser_js_data()
        )


def media_chosen(request, media_id):
    media = get_object_or_404(get_media_model(), id=media_id)

    return render_modal_workflow(
        request, None, None, None,
        json_data={
            'step':'media-chosen',
            'result': get_media_result_data(media)
        }
    )

@permission_checker.require('add')
def chooser_upload(request):
    Media = get_media_model()
    MediaForm = get_media_form(Media)

    if request.method == 'POST':
        media = Media(uploaded_by_user=request.user)
        form = MediaForm(request.POST, request.FILES, instance=media, user=request.user)

        if form.is_valid():
            form.save()
            # Reindex the media to make sure all tags are indexed
            search_index.insert_or_update_object(media)

            return render_modal_workflow(
                request, None, None,
                None, json_data={'step': 'media_chosen', 'result': get_media_result_data(media)}
            )
    else:
        form = MediaForm(user=request.user)

    media_files = Media.objects.order_by('-created_at')

    # allow hooks to modify the queryset
    for hook in hooks.get_hooks('construct_media_chooser_queryset'):
        media_files = hook(media_files, request)

    paginator, media_files = paginate(request, media_files, per_page=12)

    context = get_chooser_context(request)
    context.update({
        'media_files': media_files,
        'uploadform': form,
    })
    return render_modal_workflow(
        request, 'wagtailmedia/chooser/chooser.html', None, context,
        json_data=get_chooser_js_data()
    )
