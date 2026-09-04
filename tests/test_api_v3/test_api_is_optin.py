from wagtail import VERSION as WAGTAIL_VERSION


if WAGTAIL_VERSION >= (8, 0):
    from unittest import skipIf

    from django.conf import settings
    from django.urls import NoReverseMatch, reverse
    from wagtail.api.v3.registry import registry

    from wagtailmedia import get_media_model

    from .base import TestV3MediaBase

    Media = get_media_model()

    @skipIf(settings.ENABLE_API_V3, "Skipped as testing with ENABLE_API_V3=True")
    class TestAPIv3IsOptIn(TestV3MediaBase):
        def test_schema_not_registered(self):
            registration = registry.get(Media._meta.label)
            self.assertIsNone(registration)

        def test_schema_discovery_endpoint_doesnt_list_media(self):
            self.login()
            response = self.client.get(reverse("wagtailapi_v3:list_schemas"))
            names = [entry["name"] for entry in response.json()["types"]]
            self.assertNotIn(Media._meta.label, names)

        def test_route_not_registered(self):
            with self.assertRaises(NoReverseMatch):
                reverse("wagtailapi_v3:list_media")
