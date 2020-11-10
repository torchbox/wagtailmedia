from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from wagtail import VERSION as WAGTAIL_VERSION
from wagtail.admin.modal_workflow import render_modal_workflow
from wagtail.core import hooks
from wagtail.core.models import Collection
from wagtail.search.backends import get_search_backends

from wagtailmedia.forms import get_media_form
from wagtailmedia.models import get_media_model
from wagtailmedia.permissions import permission_policy
from wagtailmedia.utils import paginate


if WAGTAIL_VERSION < (2, 5):
    from wagtail.admin.forms import SearchForm

    pagination_template = "wagtailadmin/shared/pagination_nav.html"
else:
    from wagtail.admin.forms.search import SearchForm

    pagination_template = "wagtailadmin/shared/ajax_pagination_nav.html"

if WAGTAIL_VERSION < (2, 9):
    from wagtail.admin.utils import PermissionPolicyChecker
else:
    from wagtail.admin.auth import PermissionPolicyChecker

permission_checker = PermissionPolicyChecker(permission_policy)


def get_media_json(media):
    """
    helper function: given a media, return the json to pass back to the
    chooser panel
    """

    return {
        "id": media.id,
        "title": media.title,
        "edit_link": reverse("wagtailmedia:edit", args=(media.id,)),
    }


def chooser(request):
    media_files = permission_policy.instances_user_has_any_permission_for(
        request.user, ["change", "delete"]
    )

    # allow hooks to modify the queryset
    for hook in hooks.get_hooks("construct_media_chooser_queryset"):
        media_files = hook(media_files, request)

    if permission_policy.user_has_permission(request.user, "add"):
        Media = get_media_model()
        MediaForm = get_media_form(Media)
        uploadform = MediaForm(user=request.user, prefix="media-chooser-upload")
    else:
        uploadform = None

    q = None
    is_searching = False
    if "q" in request.GET or "p" in request.GET or "collection_id" in request.GET:
        collection_id = request.GET.get("collection_id")
        if collection_id:
            media_files = media_files.filter(collection=collection_id)

        searchform = SearchForm(request.GET)
        if searchform.is_valid():
            q = searchform.cleaned_data["q"]

            media_files = media_files.search(q)
            is_searching = True
        else:
            media_files = media_files.order_by("-created_at")
            is_searching = False

        # Pagination
        paginator, media_files = paginate(request, media_files, per_page=10)

        return render(
            request,
            "wagtailmedia/chooser/results.html",
            {
                "media_files": media_files,
                "query_string": q,
                "is_searching": is_searching,
                "pagination_template": pagination_template,
            },
        )
    else:
        searchform = SearchForm()

        collections = Collection.objects.all()
        if len(collections) < 2:
            collections = None

        media_files = media_files.order_by("-created_at")
        paginator, media_files = paginate(request, media_files, per_page=10)

    return render_modal_workflow(
        request,
        "wagtailmedia/chooser/chooser.html",
        None,
        {
            "media_files": media_files,
            "searchform": searchform,
            "collections": collections,
            "uploadform": uploadform,
            "is_searching": False,
            "pagination_template": pagination_template,
        },
        json_data={
            "step": "chooser",
            "error_label": "Server Error",
            "error_message": "Report this error to your webmaster with the following information:",
            "tag_autocomplete_url": reverse("wagtailadmin_tag_autocomplete"),
        },
    )


def media_chosen(request, media_id):
    media = get_object_or_404(get_media_model(), id=media_id)

    return render_modal_workflow(
        request,
        None,
        None,
        None,
        json_data={"step": "media_chosen", "result": get_media_json(media)},
    )


@permission_checker.require("add")
def chooser_upload(request, media_type):
    Media = get_media_model()
    MediaForm = get_media_form(Media)

    if request.method == "POST":
        media = Media(uploaded_by_user=request.user, type=media_type)
        form = MediaForm(
            request.POST,
            request.FILES,
            instance=media,
            user=request.user,
            prefix="media-chooser-upload",
        )
        if form.is_valid():
            form.save()

            # Reindex the media entry to make sure all tags are indexed
            for backend in get_search_backends():
                backend.add(media)

            return render_modal_workflow(
                request,
                None,
                None,
                None,
                json_data={"step": "media_chosen", "result": get_media_json(media)},
            )

    media_files = permission_policy.instances_user_has_any_permission_for(
        request.user, ["change", "delete"]
    )

    # allow hooks to modify the queryset
    for hook in hooks.get_hooks("construct_media_chooser_queryset"):
        media_files = hook(media_files, request)

    searchform = SearchForm()

    collections = Collection.objects.all()
    if len(collections) < 2:
        collections = None

    media_files = media_files.order_by("-created_at")
    paginator, media_files = paginate(request, media_files, per_page=10)

    context = {
        "media_files": media_files,
        "searchform": searchform,
        "collections": collections,
        "uploadform": form,
        "is_searching": False,
        "pagination_template": pagination_template,
        "media_type": media_type,
    }
    return render_modal_workflow(
        request,
        "wagtailmedia/chooser/chooser.html",
        None,
        context,
        json_data={"step": "chooser"},
    )
