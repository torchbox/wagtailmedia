from typing import Literal, cast

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Body, File, Form, Query, Router, Status, UploadedFile
from ninja.pagination import paginate
from pydantic import BaseModel
from wagtail.actions import action_registry
from wagtail.api.v3.auth import AllowAnonymous, BearerTokenAuth
from wagtail.api.v3.pagination import WagtailLimitOffsetPagination
from wagtail.api.v3.permissions import (
    get_restricted_collection_ids,
    require_any_permission,
)
from wagtail.api.v3.registry import ContentTypeRegistration, registry
from wagtail.api.v3.schemas.params import (
    APIFieldFilterSchema,
    OrderingSchema,
    SearchSchema,
)

from wagtailmedia import get_media_model

from .form_data import build_media_form, build_media_update_form


router = Router(tags=["media"])
Media = get_media_model()
registered_schemas = cast(ContentTypeRegistration, registry.get(Media._meta.label))
MediaDetailSchema = cast(type[BaseModel], registered_schemas.read_schema)
MediaCreateSchema = cast(type[BaseModel], registered_schemas.create_schema)
MediaPatchSchema = cast(type[BaseModel], registered_schemas.patch_schema)
BASE_MEDIA_READ_FIELDS = ["id", "title"]


def get_media_queryset(request: HttpRequest):
    restricted_collection_ids = get_restricted_collection_ids(request)
    return (
        Media.objects.exclude(collection__in=restricted_collection_ids)
        .prefetch_related("tags")
        .order_by("id")
    )


@router.get(
    "/",
    response=list[MediaDetailSchema],  # ty: ignore[invalid-type-form]
    url_name="list_media",
    summary="List media",
    operation_id="media_list",
    auth=[BearerTokenAuth(), AllowAnonymous()],
)
@paginate(
    WagtailLimitOffsetPagination,
    pass_parameter="pagination_info",  # noqa: S106 not a password
)
def list_media(
    request: HttpRequest,
    ordering: OrderingSchema = Query(...),  # noqa: B008 ty: ignore[call-non-callable]
    search: SearchSchema = Query(...),  # noqa: B008 ty: ignore[call-non-callable]
    **kwargs,
):
    pagination_info = cast(
        WagtailLimitOffsetPagination.Input,
        kwargs.get("pagination_info"),
    )
    field_filter = APIFieldFilterSchema.with_exclude_schemas(
        raw_params=request.GET,
        schemas=(OrderingSchema, SearchSchema),
        base_fields=BASE_MEDIA_READ_FIELDS,
    )
    queryset = get_media_queryset(request)
    queryset = field_filter.filter_queryset(queryset)
    queryset = ordering.order_queryset(
        queryset,
        pagination_info,
        base_fields=BASE_MEDIA_READ_FIELDS,
    )
    queryset = search.search_queryset(request, queryset)
    return queryset


@router.get(
    "/{media_id}/",
    response=MediaDetailSchema,
    url_name="detail_media",
    summary="Media detail",
    operation_id="media_detail",
    auth=[BearerTokenAuth(), AllowAnonymous()],
)
def get_media_item(request: HttpRequest, media_id: int):
    return get_object_or_404(get_media_queryset(request), pk=media_id)


@router.post(
    "/{media_type}",
    response={201: MediaDetailSchema},
    url_name="create_media",
    summary="Create media",
    operation_id="media_create",
    auth=BearerTokenAuth(),
)
@require_any_permission(Media, ("add",))
def create_media(
    request: HttpRequest,
    media_type: Literal["audio", "video"],
    file: UploadedFile = File(...),  # noqa: B008 ty: ignore[call-non-callable]
    data: MediaCreateSchema = Form(...),  # noqa: B008 ty: ignore[call-non-callable, invalid-type-form]
):
    form = build_media_form(Media, media_type, data, file, request.user)
    action_class = action_registry.get_action_class(Media, "create")
    action = action_class(form.instance, user=request.user, form=form)
    action.execute()
    return Status(201, form.instance)


@router.patch(
    "/{media_id}/",
    response=MediaDetailSchema,
    url_name="update_media",
    summary="Update media",
    operation_id="media_update",
    auth=BearerTokenAuth(),
)
@require_any_permission(Media, ("change",))
def update_media(
    request: HttpRequest,
    media_id: int,
    data: MediaPatchSchema = Body(...),  # noqa: B008 ty: ignore[call-non-callable, invalid-type-form]
):
    media_item = get_object_or_404(Media, pk=media_id)
    form = build_media_update_form(media_item, data, request.user)
    action_class = action_registry.get_action_class(Media, "edit")
    action = action_class(form.instance, user=request.user, form=form)
    action.execute()
    return form.instance


@router.delete(
    "/{media_id}/",
    response={204: None},
    url_name="delete_media",
    summary="Delete media",
    operation_id="media_delete",
    auth=BearerTokenAuth(),
)
@require_any_permission(Media, ("delete",))
def delete_media(request: HttpRequest, media_id: int):
    media_item = get_object_or_404(Media, pk=media_id)
    action_class = action_registry.get_action_class(Media, "delete")
    action = action_class(media_item, user=request.user)
    action.execute()
    return Status(204, None)
