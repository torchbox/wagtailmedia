from wagtail import VERSION as WAGTAIL_VERSION


if WAGTAIL_VERSION >= (8, 0):
    import json

    from unittest import mock, skipUnless

    from django.conf import settings
    from django.db.models.signals import post_save
    from django.urls import reverse

    from wagtailmedia import get_media_model

    from .base import TestV3MediaBase

    Media = get_media_model()

    @skipUnless(settings.ENABLE_API_V3, "Skipped as testing with ENABLE_API_V3=False")
    class TestV3MediaUpdate(TestV3MediaBase):
        def setUp(self):
            super().setUp()
            self.media = self.create_media(title="Original")

        def patch(self, media_id, data):
            return self.client.patch(
                reverse(
                    "wagtailapi_v3:update_media",
                    kwargs={"media_id": media_id},
                ),
                data=json.dumps(data),
                content_type="application/json",
            )

        def test_anonymous_returns_401(self):
            response = self.patch(self.media.id, {"title": "Changed"})
            self.assert_problem_response(response, status_code=401)

        def test_superuser_can_update_title(self):
            self.login()
            response = self.patch(self.media.id, {"title": "Changed"})
            self.assertEqual(response.status_code, 200)
            self.media.refresh_from_db()
            self.assertEqual(self.media.title, "Changed")

        def test_partial_update_leaves_collection_and_file_unchanged(self):
            self.login()
            original = (
                self.media.collection_id,
                self.media.file.name,
            )
            response = self.patch(self.media.id, {"title": "Metadata only"})
            self.assertEqual(response.status_code, 200)
            self.media.refresh_from_db()
            self.assertEqual(
                (
                    self.media.collection_id,
                    self.media.file.name,
                ),
                original,
            )

        def test_update_collection_to_permitted_collection(self):
            user = self.create_user(username="editor", password="password")
            old_collection = self.media.collection
            new_collection = self.create_collection("New home")
            self.grant_collection_permission(user, old_collection, "change_media")
            self.grant_collection_permission(user, new_collection, "add_media")
            self.authorize(user)
            response = self.patch(
                self.media.id,
                {"collection_id": new_collection.id},
            )
            self.assertEqual(response.status_code, 200)
            self.media.refresh_from_db()
            self.assertEqual(self.media.collection_id, new_collection.id)

        def test_update_to_forbidden_collection_returns_422(self):
            user = self.create_user(username="limited-editor", password="password")
            self.grant_collection_permission(
                user, self.media.collection, "change_media"
            )
            self.grant_collection_permission(
                user, self.create_collection("Allowed"), "add_media"
            )
            self.grant_collection_permission(
                user,
                self.create_collection("Also allowed"),
                "add_media",
            )
            forbidden = self.create_collection("Forbidden")
            self.authorize(user)
            response = self.patch(
                self.media.id,
                {"collection_id": forbidden.id},
            )
            self.assert_problem_response(
                response,
                status_code=422,
                errors=[{"loc": ["collection"]}],
            )

        def test_update_to_forbidden_collection_with_single_choice_returns_422(self):
            user = self.create_user(
                username="single-choice-editor", password="password"
            )
            self.grant_collection_permission(
                user, self.media.collection, "change_media"
            )
            forbidden = self.create_collection("Forbidden")
            self.authorize(user)
            response = self.patch(
                self.media.id,
                {"collection_id": forbidden.id},
            )
            self.assert_problem_response(
                response,
                status_code=422,
                errors=[{"loc": ["collection"]}],
            )

        def test_uploader_with_add_permission_can_edit_own_media(self):
            user = self.create_user(username="uploader", password="password")
            self.grant_collection_permission(user, self.media.collection, "add_media")
            self.media.uploaded_by_user = user
            self.media.save(update_fields=["uploaded_by_user"])
            self.authorize(user)
            response = self.patch(self.media.id, {"title": "Mine"})
            self.assertEqual(response.status_code, 200)

        def test_cannot_edit_other_users_media_without_change_permission(self):
            owner = self.create_user(username="owner", password="password")
            user = self.create_user(username="other", password="password")
            self.grant_collection_permission(user, self.media.collection, "add_media")
            self.media.uploaded_by_user = owner
            self.media.save(update_fields=["uploaded_by_user"])
            self.authorize(user)
            response = self.patch(self.media.id, {"title": "Not mine"})
            self.assert_problem_response(
                response,
                status_code=403,
                detail_contains=(
                    "You do not have permission to perform the 'edit' "
                    "action on this object."
                ),
            )

        def test_unknown_id_returns_404(self):
            self.login()
            self.assertEqual(self.patch(999999, {"title": "Missing"}).status_code, 404)

        def test_audit_log(self):
            self.login()
            self.patch(self.media.id, {"title": "Logged"})
            self.assert_log_actions(self.media, ["wagtail.edit"])

        def test_post_save_signal_fires_once(self):
            handler = mock.MagicMock()
            post_save.connect(handler, sender=Media)
            try:
                self.login()
                response = self.patch(self.media.id, {"title": "Signalled"})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(handler.call_count, 1)
            finally:
                post_save.disconnect(handler, sender=Media)
