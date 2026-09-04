from wagtail import VERSION as WAGTAIL_VERSION


if WAGTAIL_VERSION >= (8, 0):
    from unittest import skipUnless

    from django.conf import settings
    from django.urls import reverse
    from wagtail.api.v3.registry import registry

    from wagtailmedia import get_media_model
    from wagtailmedia.api.v3.schemas import build_media_schemas

    from .base import TestV3MediaBase

    Media = get_media_model()

    @skipUnless(settings.ENABLE_API_V3, "Skipped as testing with ENABLE_API_V3=False")
    class TestV3MediaSchemas(TestV3MediaBase):
        def test_content_type_registered_for_schema_discovery(self):
            registration = registry.get(Media._meta.label)
            self.assertIsNotNone(registration)
            self.assertEqual(
                set(registry.get_type_schemas(Media._meta.label)),
                {"read", "create", "patch"},
            )

        def test_schema_discovery_endpoint_lists_medias(self):
            self.login()
            response = self.client.get(reverse("wagtailapi_v3:list_schemas"))
            names = [entry["name"] for entry in response.json()["types"]]
            self.assertIn(Media._meta.label, names)

        def test_read_schema_shape(self):
            read_schema, _, _ = build_media_schemas()
            properties = read_schema.model_json_schema()["properties"]
            self.assertLessEqual(
                {"id", "title", "collection", "meta"}, properties.keys()
            )

        def test_read_meta_fields(self):
            read_schema, _, _ = build_media_schemas()
            meta = read_schema.model_fields["meta"].annotation
            self.assertEqual(meta.__name__, "MediaDetailMetaSchema")
            self.assertLessEqual(
                {"type", "detail_url", "tags", "download_url"},
                meta.model_json_schema()["properties"].keys(),
            )

        def test_create_schema_fields(self):
            _, create_schema, _ = build_media_schemas()
            self.assertIn("title", create_schema.model_fields)
            self.assertIn(
                "collection_id", create_schema.model_json_schema()["properties"]
            )
            self.assertNotIn("file", create_schema.model_fields)
            self.assertNotIn("tags", create_schema.model_fields)
            self.assertTrue(create_schema.model_fields["title"].is_required())

        def test_patch_schema_fields_are_optional(self):
            _, _, patch_schema = build_media_schemas()
            self.assertNotIn("file", patch_schema.model_fields)
            self.assertNotIn("tags", patch_schema.model_fields)
            for field in patch_schema.model_fields.values():
                self.assertFalse(field.is_required())
