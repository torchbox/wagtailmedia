from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.auth import PermissionPolicyChecker
from wagtail.admin.forms.search import SearchForm
from wagtail.admin.modal_workflow import render_modal_workflow
from wagtail.admin.models import popular_tags_for_model
from wagtail.models import Collection
from wagtail.search.backends import get_search_backends

from wagtailmedia.forms import get_media_form
from wagtailmedia.models import get_media_model
from wagtailmedia.permissions import permission_policy
from wagtailmedia.utils import paginate


pagination_template = "wagtailadmin/shared/ajax_pagination_nav.html"
permission_checker = PermissionPolicyChecker(permission_policy)


def get_media_json(media):
    """
    helper function: given a media, return the json to pass back to the
    chooser panel
    """

    return {
        "id": media.id,
        "title": media.title,
        "edit_url": reverse("wagtailmedia:edit", args=(media.id,)),
    }


def get_ordering(request):
    if request.GET.get("ordering") in ["title", "-title", "-created_at", "created_at"]:
        return request.GET["ordering"]

    # default to -created_at
    return "-created_at"


def chooser(request, media_type=None):
    Media = get_media_model()

    ordering = get_ordering(request)
    media_files = permission_policy.instances_user_has_any_permission_for(
        request.user, ["change", "delete"]
    )

    # allow hooks to modify the queryset
    for hook in hooks.get_hooks("construct_media_chooser_queryset"):
        media_files = hook(media_files, request)

    if permission_policy.user_has_permission(request.user, "add"):
        MediaForm = get_media_form(Media)
        media_audio = Media(uploaded_by_user=request.user, type="audio")
        media_video = Media(uploaded_by_user=request.user, type="video")

        uploadforms = {
            "audio": MediaForm(
                user=request.user, prefix="media-chooser-upload", instance=media_audio
            ),
            "video": MediaForm(
                user=request.user, prefix="media-chooser-upload", instance=media_video
            ),
        }

        if media_type:
            uploadforms = {media_type: uploadforms[media_type]}
    else:
        uploadforms = {}

    if media_type:
        media_files = media_files.filter(type=media_type)

    if (
        "q" in request.GET
        or "p" in request.GET
        or "tag" in request.GET
        or "collection_id" in request.GET
    ):
        collection_id = request.GET.get("collection_id")
        if collection_id:
            media_files = media_files.filter(collection=collection_id)

        searchform = SearchForm(request.GET)
        if searchform.is_valid() and searchform.cleaned_data["q"]:
            q = searchform.cleaned_data["q"]

            media_files = media_files.search(q)
            is_searching = True
        else:
            media_files = media_files.order_by(ordering)
            is_searching = False
            q = None

            tag_name = request.GET.get("tag")
            if tag_name:
                media_files = media_files.filter(tags__name=tag_name)

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
                "media_type": media_type,
                "ordering": ordering,
            },
        )
    else:
        searchform = SearchForm()

        collections = Collection.objects.all()
        if len(collections) < 2:
            collections = None

        media_files = media_files.order_by(ordering)
        paginator, media_files = paginate(request, media_files, per_page=10)

    if media_type == "audio":
        title = _("Choose audio")
    elif media_type == "video":
        title = _("Choose video")
    else:
        title = _("Choose a media item")

    return render_modal_workflow(
        request,
        "wagtailmedia/chooser/chooser.html",
        None,
        {
            "media_files": media_files,
            "searchform": searchform,
            "collections": collections,
            "uploadforms": uploadforms,
            "is_searching": False,
            "pagination_template": pagination_template,
            "popular_tags": popular_tags_for_model(Media),
            "media_type": media_type,
            "ordering": ordering,
            "title": title,
            "icon": f"wagtailmedia-{media_type}" if media_type is not None else "media",
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
    upload_forms = {}

    if (
        permission_policy.user_has_permission(request.user, "add")
        and request.method == "POST"
    ):
        Media = get_media_model()
        MediaForm = get_media_form(Media)

        media = Media(uploaded_by_user=request.user, type=media_type)
        uploading_form = MediaForm(
            request.POST,
            request.FILES,
            instance=media,
            user=request.user,
            prefix="media-chooser-upload",
        )
        if uploading_form.is_valid():
            uploading_form.save()

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

        if media_type == "audio":
            video = Media(uploaded_by_user=request.user, type="video")
            video_form = MediaForm(
                instance=video, user=request.user, prefix="media-chooser-upload"
            )
            upload_forms = {"audio": uploading_form, "video": video_form}
        else:
            audio = Media(uploaded_by_user=request.user, type="audio")
            audio_form = MediaForm(
                instance=audio, user=request.user, prefix="media-chooser-upload"
            )
            upload_forms = {"audio": audio_form, "video": uploading_form}

    ordering = get_ordering(request)

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

    media_files = media_files.order_by(ordering)
    paginator, media_files = paginate(request, media_files, per_page=10)

    context = {
        "media_files": media_files,
        "searchform": searchform,
        "collections": collections,
        "uploadforms": upload_forms,
        "is_searching": False,
        "pagination_template": pagination_template,
        "media_type": media_type,
        "ordering": ordering,
    }
    return render_modal_workflow(
        request,
        "wagtailmedia/chooser/chooser.html",
        None,
        context,
        json_data={"step": "chooser"},
    )
