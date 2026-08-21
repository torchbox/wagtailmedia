from wagtail import VERSION as WAGTAIL_VERSION


if WAGTAIL_VERSION >= (8, 0):
    from unittest import mock
    from urllib.parse import urlsplit

    from django.core.files.uploadedfile import SimpleUploadedFile
    from django.db.models.signals import post_save
    from django.test import override_settings
    from django.urls import reverse

    from wagtailmedia import get_media_model
    from wagtailmedia.models import media_served

    from .base import TestV3MediaBase

    Media = get_media_model()
    FILE_CONTENTS = b"Test media contents"

    class TestV3MediaCreate(TestV3MediaBase):
        def post_media(self, **kwargs):
            data = {
                "file": SimpleUploadedFile("test.mp3", FILE_CONTENTS),
            }
            data.update(kwargs)
            return self.client.post(reverse("wagtailapi_v3:create_media"), data)

        def test_anonymous_returns_401(self):
            response = self.post_media(title="Test")
            self.assert_problem_response(response, status_code=401)

        def test_superuser_can_create(self):
            user = self.login()
            response = self.post_media(title="Uploaded media")
            self.assertEqual(response.status_code, 201)
            content = response.json()
            media = Media.objects.get(id=content["id"])
            self.assertEqual(media.title, "Uploaded media")
            self.assertEqual(media.uploaded_by_user, user)
            self.assertIn("download_url", content["meta"])

        def test_missing_title_returns_422(self):
            self.login()
            self.assert_problem_response(self.post_media(), status_code=422)

        def test_missing_file_returns_422(self):
            self.login()
            response = self.client.post(
                reverse("wagtailapi_v3:create_media"),
                {"title": "No file"},
            )
            self.assert_problem_response(response, status_code=422)

        def test_user_without_add_permission_gets_403(self):
            user = self.create_user(username="noperms", password="password")
            self.authorize(user)
            response = self.post_media(title="Forbidden")
            self.assert_problem_response(
                response,
                status_code=403,
                detail_contains="Permission denied",
            )

        def test_single_permitted_collection_is_selected(self):
            user = self.create_user(username="adder", password="password")
            collection = self.create_collection("Only choice")
            self.grant_collection_permission(user, collection, "add_media")
            self.authorize(user)
            response = self.post_media(title="In only choice")
            self.assertEqual(response.status_code, 201)
            self.assertEqual(
                Media.objects.get(id=response.json()["id"]).collection_id,
                collection.id,
            )

        def test_missing_collection_with_multiple_choices_returns_422(self):
            user = self.create_user(username="multi", password="password")
            self.grant_collection_permission(
                user, self.create_collection("First"), "add_media"
            )
            self.grant_collection_permission(
                user, self.create_collection("Second"), "add_media"
            )
            self.authorize(user)
            response = self.post_media(title="Missing collection")
            self.assert_problem_response(
                response,
                status_code=422,
                errors=[{"loc": ["collection"]}],
            )

        def test_forbidden_collection_returns_422(self):
            user = self.create_user(username="limited", password="password")
            self.grant_collection_permission(
                user, self.create_collection("Allowed"), "add_media"
            )
            self.grant_collection_permission(
                user, self.create_collection("Also allowed"), "add_media"
            )
            forbidden = self.create_collection("Forbidden")
            self.authorize(user)
            response = self.post_media(
                title="Wrong collection",
                collection_id=forbidden.id,
            )
            self.assert_problem_response(
                response,
                status_code=422,
                errors=[{"loc": ["collection"]}],
            )

        def test_forbidden_collection_with_single_choice_returns_422(self):
            user = self.create_user(username="single-limited", password="password")
            self.grant_collection_permission(
                user, self.create_collection("Only allowed"), "add_media"
            )
            forbidden = self.create_collection("Forbidden")
            self.authorize(user)
            response = self.post_media(
                title="Wrong collection",
                collection_id=forbidden.id,
            )
            self.assert_problem_response(
                response,
                status_code=422,
                errors=[{"loc": ["collection"]}],
            )

        @override_settings(
            WAGTAILMEDIA={"VIDEO_EXTENSIONS": ["mov"], "AUDIO_EXTENSIONS": ["wav"]}
        )
        def test_bad_extension_returns_422(self):
            self.login()
            response = self.post_media(title="Wrong extension")
            self.assert_problem_response(
                response,
                status_code=422,
                errors=[{"loc": ["file"]}],
            )

        def test_audit_log(self):
            self.login()
            response = self.post_media(title="Logged")
            media = Media.objects.get(id=response.json()["id"])
            self.assert_log_actions(media, ["wagtail.create"])

        def test_post_save_signal_fires_once(self):
            handler = mock.MagicMock()
            post_save.connect(handler, sender=Media)
            try:
                self.login()
                response = self.post_media(title="Signalled")
                self.assertEqual(response.status_code, 201)
                self.assertEqual(handler.call_count, 1)
            finally:
                post_save.disconnect(handler, sender=Media)

        def test_api_uploaded_media_can_be_served(self):
            handler = mock.MagicMock()
            media_served.connect(handler)
            try:
                self.login()
                create_response = self.post_media(title="Served")
                url = create_response.json()["meta"]["download_url"]
                response = self.client.get(urlsplit(url).path)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(b"".join(response.streaming_content), FILE_CONTENTS)
                self.assertEqual(handler.call_count, 1)
            finally:
                media_served.disconnect(handler)
