from wagtail import VERSION as WAGTAIL_VERSION


if WAGTAIL_VERSION >= (8, 0):
    from django.urls import reverse
    from wagtail.models import CollectionViewRestriction

    from .base import TestV3MediaBase

    class TestV3MediaDetail(TestV3MediaBase):
        def get_response(self, media_id):
            return self.client.get(
                reverse(
                    "wagtailapi_v3:detail_media",
                    kwargs={"media_id": media_id},
                )
            )

        def test_anonymous_can_get_detail(self):
            media = self.create_media(title="Public media")
            response = self.get_response(media.id)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["id"], media.id)
            self.assertEqual(response.json()["title"], "Public media")

        def test_direct_restriction_returns_404(self):
            collection = self.create_collection("Restricted")
            media = self.create_media(collection=collection)
            CollectionViewRestriction.objects.create(
                collection=collection,
                restriction_type=CollectionViewRestriction.LOGIN,
            )
            self.assertEqual(self.get_response(media.id).status_code, 404)

        def test_ancestor_restriction_returns_404(self):
            parent = self.create_collection("Restricted parent")
            child = self.create_collection("Child", parent=parent)
            media = self.create_media(collection=child)
            CollectionViewRestriction.objects.create(
                collection=parent,
                restriction_type=CollectionViewRestriction.LOGIN,
            )
            self.assertEqual(self.get_response(media.id).status_code, 404)

        def test_unknown_id_returns_404(self):
            self.assertEqual(self.get_response(999999).status_code, 404)
