from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WagtailMediaAppConfig(AppConfig):
    name = 'wagtailmedia'
    label = 'wagtailmedia'
    verbose_name = _("Wagtail media")

    def ready(self):
        from wagtailmedia.signal_handlers import register_signal_handlers
        register_signal_handlers()
