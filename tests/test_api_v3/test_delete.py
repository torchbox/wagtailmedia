from wagtail import VERSION as WAGTAIL_VERSION


if WAGTAIL_VERSION >= (8, 0):
    from unittest import mock, skipUnless

    from django.conf import settings
    from django.db.models.signals import post_delete
    from django.urls import reverse

    from wagtailmedia import get_media_model

    from .base import TestV3MediaBase

    Media = get_media_model()

    @skipUnless(settings.ENABLE_API_V3, "Skipped as testing with ENABLE_API_V3=False")
    class TestV3MediaDelete(TestV3MediaBase):
        def delete(self, media_id):
            return self.client.delete(
                reverse(
                    "wagtailapi_v3:delete_media",
                    kwargs={"media_id": media_id},
                )
            )

        def test_anonymous_returns_401(self):
            media = self.create_media()
            self.assert_problem_response(self.delete(media.id), status_code=401)

        def test_superuser_can_delete(self):
            self.login()
            media = self.create_media()
            response = self.delete(media.id)
            self.assertEqual(response.status_code, 204)
            self.assertFalse(Media.objects.filter(id=media.id).exists())

        def test_user_without_delete_permission_gets_403(self):
            media = self.create_media()
            user = self.create_user(username="other", password="password")
            self.grant_collection_permission(user, media.collection, "add_media")
            self.authorize(user)
            response = self.delete(media.id)
            self.assert_problem_response(
                response,
                status_code=403,
                detail_contains=(
                    "You do not have permission to perform the 'delete' "
                    "action on this object."
                ),
            )

        def test_uploader_with_add_permission_can_delete_own_media(self):
            user = self.create_user(username="uploader", password="password")
            media = self.create_media(uploaded_by_user=user)
            self.grant_collection_permission(user, media.collection, "add_media")
            self.authorize(user)
            response = self.delete(media.id)
            self.assertEqual(response.status_code, 204)
            self.assertFalse(Media.objects.filter(id=media.id).exists())

        def test_unknown_id_returns_404(self):
            self.login()
            self.assertEqual(self.delete(999999).status_code, 404)

        def test_audit_log(self):
            self.login()
            media = self.create_media(title="Logged")
            self.delete(media.id)
            self.assert_log_actions(media, ["wagtail.delete"])

        def test_post_delete_signal_fires_once(self):
            handler = mock.MagicMock()
            post_delete.connect(handler, sender=Media)
            try:
                self.login()
                media = self.create_media()
                response = self.delete(media.id)
                self.assertEqual(response.status_code, 204)
                self.assertEqual(handler.call_count, 1)
            finally:
                post_delete.disconnect(handler, sender=Media)

        def test_stored_file_is_deleted_on_commit(self):
            self.login()
            media = self.create_media()
            storage = media.file.storage
            name = media.file.name
            self.assertTrue(storage.exists(name))
            with self.captureOnCommitCallbacks(execute=True):
                response = self.delete(media.id)
            self.assertEqual(response.status_code, 204)
            self.assertFalse(storage.exists(name))
