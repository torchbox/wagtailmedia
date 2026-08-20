from django.apps import AppConfig
from django.db.models import ForeignKey
from wagtail import VERSION as WAGTAIL_VERSION


class WagtailMediaAppConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "wagtailmedia"
    label = "wagtailmedia"
    verbose_name = "Wagtail media"

    def ready(self):
        from wagtail.admin.compare import register_comparison_class

        from . import get_media_model
        from .edit_handlers import MediaFieldComparison
        from .signal_handlers import register_signal_handlers

        register_signal_handlers()

        # Set up image ForeignKeys to use MediaFieldComparison as the comparison class
        # when comparing page revisions
        register_comparison_class(
            ForeignKey, to=get_media_model(), comparison_class=MediaFieldComparison
        )

        if WAGTAIL_VERSION >= (8, 0):
            from wagtail.permissions import register_permission_policy

            from .permissions import get_permission_policy

            register_permission_policy(get_media_model(), get_permission_policy())
