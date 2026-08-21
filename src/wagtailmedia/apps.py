from django.apps import AppConfig
from django.db.models import ForeignKey
from wagtail import VERSION as WAGTAIL_VERSION

from . import get_media_model, get_permission_policy


class WagtailMediaAppConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "wagtailmedia"
    label = "wagtailmedia"
    verbose_name = "Wagtail media"

    def ready(self):
        from wagtail.admin.compare import register_comparison_class

        from .edit_handlers import MediaFieldComparison
        from .signal_handlers import register_signal_handlers

        Media = get_media_model()
        if WAGTAIL_VERSION >= (8, 0):
            from wagtail.permissions import register_permission_policy

            register_permission_policy(Media, get_permission_policy())

        register_signal_handlers()

        # Set up image ForeignKeys to use MediaFieldComparison as the comparison class
        # when comparing page revisions
        register_comparison_class(
            ForeignKey, to=Media, comparison_class=MediaFieldComparison
        )

        if WAGTAIL_VERSION >= (8, 0):
            # v3 API. Note: the import order matters
            from .api.v3.registry import register_content_types

            register_content_types()

            from wagtail.api.v3.api import api

            from .api.v3.router import router

            api.add_router("/media/", router)
