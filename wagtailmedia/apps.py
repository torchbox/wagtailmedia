from django.apps import AppConfig


class WagtailMediaAppConfig(AppConfig):
    name = "wagtailmedia"
    label = "wagtailmedia"
    verbose_name = "Wagtail media"

    def ready(self):
        from wagtailmedia.signal_handlers import register_signal_handlers

        register_signal_handlers()
