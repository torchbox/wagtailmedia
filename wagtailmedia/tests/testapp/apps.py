from django.apps import AppConfig


class WagtailmediaTestsAppConfig(AppConfig):
    name = "wagtailmedia.tests.testapp"
    label = "wagtailmedia_tests"
    verbose_name = "Wagtail media tests"
    default_auto_field = "django.db.models.AutoField"
