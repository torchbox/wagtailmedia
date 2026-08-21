from wagtail import VERSION as WAGTAIL_VERSION


if WAGTAIL_VERSION >= (8, 0):
    from unittest.mock import patch

    from django.contrib.auth.models import Group, Permission
    from django.core.files.uploadedfile import SimpleUploadedFile
    from django.test import TestCase, override_settings
    from ninja import Schema
    from testapp.models import CustomMedia
    from wagtail.actions import CreateAction
    from wagtail.api import APIField
    from wagtail.api.v3.schemas import create_generator, patch_generator
    from wagtail.models import Collection, GroupCollectionPermission
    from wagtail.test.utils import WagtailTestUtils

    from wagtailmedia.api.v3 import schemas as media_schemas
    from wagtailmedia.api.v3.form_data import build_media_form
    from wagtailmedia.forms import get_media_form

    @override_settings(WAGTAILMEDIA={"MEDIA_MODEL": "wagtailmedia_tests.CustomMedia"})
    class TestV3CustomMediaModel(WagtailTestUtils, TestCase):
        @classmethod
        def setUpTestData(cls):
            from wagtail.permissions import register_permission_policy

            from wagtailmedia import get_media_model, get_permission_policy

            register_permission_policy(get_media_model(), get_permission_policy())

            cls.user = cls.create_user(username="uploader", password="password")
            group = Group.objects.create(name="custom media uploaders")
            cls.user.groups.add(group)
            permission = Permission.objects.get(
                content_type__app_label="wagtailmedia",
                codename="add_media",
            )
            GroupCollectionPermission.objects.create(
                group=group,
                collection=Collection.get_first_root_node(),
                permission=permission,
            )
            cls.fields = [
                name
                for name in CustomMedia.admin_form_fields
                if name not in {"file", "tags"}
            ]

        def create_schema(self):
            return create_generator.generate_schema(
                CustomMedia,
                base_class=Schema,
                fields=self.fields,
                required_fields=("title",),
            )

        def test_create_schema_includes_custom_admin_form_fields(self):
            schema = self.create_schema()
            self.assertIn("fancy_caption", schema.model_fields)
            self.assertNotIn("file", schema.model_fields)
            self.assertNotIn("tags", schema.model_fields)

        def test_patch_schema_includes_custom_admin_form_fields(self):
            schema = patch_generator.generate_schema(
                CustomMedia,
                base_class=Schema,
                fields=self.fields,
            )
            self.assertIn("fancy_caption", schema.model_fields)
            self.assertTrue(
                all(not field.is_required() for field in schema.model_fields.values())
            )

        def test_media_input_schemas_include_writable_api_fields(self):
            admin_form_fields = tuple(
                field
                for field in CustomMedia.admin_form_fields
                if field not in {"file", "tags"}
            )
            input_fields = [
                field for field in admin_form_fields if field not in {"file", "tags"}
            ]
            writable_api_fields = (
                APIField("file", writable=True),
                APIField("tags", writable=True),
                APIField("fancy_caption", writable=True),
            )

            with (
                patch.object(CustomMedia, "admin_form_fields", admin_form_fields),
                patch.object(
                    CustomMedia, "api_fields", writable_api_fields, create=True
                ),
                patch.object(media_schemas, "Media", CustomMedia),
                patch.object(media_schemas, "BASE_MEDIA_FIELDS", input_fields),
            ):
                _, create_schema, patch_schema = media_schemas.build_media_schemas()

            for schema in (create_schema, patch_schema):
                self.assertIn("fancy_caption", schema.model_fields)
                self.assertIn("file", schema.model_fields)
                self.assertIn("tags", schema.model_fields)

        def test_media_form_binds_custom_fields(self):
            form_class = get_media_form(CustomMedia)
            self.assertIn("fancy_caption", form_class.base_fields)

        def test_create_action_saves_custom_media_and_metadata(self):
            data = self.create_schema().model_validate(
                {
                    "title": "Custom",
                    "fancy_caption": "<p>Fancy description</p>",
                }
            )
            form = build_media_form(
                CustomMedia,
                data,
                SimpleUploadedFile("custom.mp3", b"Custom contents"),
                self.user,
            )
            self.assertFalse(form.errors)
            CreateAction(form.instance, user=self.user, form=form).execute()
            media = CustomMedia.objects.get(title="Custom")
            self.assertRegex(
                media.fancy_caption, '<p data-block-key=".*">Fancy description</p>'
            )

        def test_custom_model_unique_constraint_returns_form_error(self):
            collection = Collection.get_first_root_node()
            CustomMedia.objects.create(
                title="Duplicate",
                file=SimpleUploadedFile("first.mp4", b"First"),
                collection=collection,
            )
            data = self.create_schema().model_validate({"title": "Duplicate"})
            form = build_media_form(
                CustomMedia,
                data,
                SimpleUploadedFile("second.mp4", b"Second"),
                self.user,
            )
            self.assertFalse(form.is_valid())
            self.assertIn("__all__", form.errors)

        @override_settings(
            WAGTAILMEDIA={
                "MEDIA_MODEL": "wagtailmedia_tests.CustomMedia",
                "MEDIA_FORM_BASE": "testapp.forms.AlternateMediaForm",
            }
        )
        def test_configured_base_form_validation_is_used(self):
            data = self.create_schema().model_validate({"title": "Custom form"})
            form = build_media_form(
                CustomMedia,
                data,
                SimpleUploadedFile("custom-form.mp3", b"Custom form contents"),
                self.user,
            )
            self.assertFalse(form.is_valid())
            self.assertIn("form_only_field", form.errors)
