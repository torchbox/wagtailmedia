import json

from django.test import TestCase, override_settings
from django.urls import reverse
from wagtail import VERSION as WAGTAIL_VERSION

from wagtailmedia.models import get_media_model

from .utils import create_audio, create_video


Media = get_media_model()


class ApiTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        with cls.captureOnCommitCallbacks(execute=True):
            cls.a_space_odyssey = create_video("2001: A Space Odyssey")
            cls.tng = create_video("Star Trek: The Next Generation")
            cls.pink_floyd_time = create_audio("Pink Floyd: Time")

    def tearDown(self) -> None:
        for item in Media.objects.all():
            item.file.delete(False)
            item.delete()


class TestApiMediaListing(ApiTestBase):
    def get_response(self, **params):
        return self.client.get(reverse("wagtailapi_v2:media:listing"), params)

    def get_media_id_list(self, content):
        return [item["id"] for item in content["items"]]

    def test_basic(self):
        response = self.get_response()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-type"], "application/json")

        # Will crash if the JSON is invalid
        content = json.loads(response.content.decode("UTF-8"))

        # Check that the meta section is there
        self.assertIn("meta", content)
        self.assertIsInstance(content["meta"], dict)

        # Check that the total count is there and correct
        self.assertIn("total_count", content["meta"])
        self.assertIsInstance(content["meta"]["total_count"], int)
        self.assertEqual(content["meta"]["total_count"], Media.objects.count())

        # Check that the items section is there
        self.assertIn("items", content)
        self.assertIsInstance(content["items"], list)

        # Check that each item has a meta section with type and detail_url attributes
        for item in content["items"]:
            self.assertIn("meta", item)
            self.assertIsInstance(item["meta"], dict)
            self.assertEqual(
                set(item["meta"].keys()),
                {"type", "detail_url", "download_url", "tags"},
            )

            # Type should always be wagtaildocs.item
            self.assertEqual(item["meta"]["type"], "wagtailmedia.Media")

            # Check detail_url
            self.assertEqual(
                item["meta"]["detail_url"], f"http://localhost/api/media/{item['id']}/"
            )

            media = Media.objects.get(pk=item["id"])
            # Check download_url
            self.assertEqual(item["meta"]["download_url"], f"/media/{media.file}")
            # Check full_url
            self.assertEqual(
                item["full_url"], f"http://localhost:8020/media/{media.file}"
            )

            self.assertEqual(item["media_type"], media.type)

    def test_fields_default(self):
        response = self.get_response()
        content = json.loads(response.content.decode("UTF-8"))

        for item in content["items"]:
            self.assertEqual(
                set(item.keys()),
                {
                    "id",
                    "meta",
                    "title",
                    "width",
                    "height",
                    "media_type",
                    "collection",
                    "full_url",
                },
            )
            self.assertEqual(
                set(item["meta"].keys()),
                {"type", "detail_url", "download_url", "tags"},
            )

    def test_fields(self):
        response = self.get_response(fields="title")
        content = json.loads(response.content.decode("UTF-8"))

        for item in content["items"]:
            self.assertEqual(
                set(item.keys()),
                {
                    "id",
                    "meta",
                    "title",
                    "width",
                    "height",
                    "media_type",
                    "collection",
                    "full_url",
                },
            )
            self.assertEqual(
                set(item["meta"].keys()),
                {"type", "detail_url", "download_url", "tags"},
            )

    def test_remove_fields(self):
        response = self.get_response(fields="-title,-collection")
        content = json.loads(response.content.decode("UTF-8"))

        for item in content["items"]:
            self.assertEqual(
                set(item.keys()),
                {"id", "meta", "width", "height", "media_type", "full_url"},
            )

    def test_remove_meta_fields(self):
        response = self.get_response(fields="-download_url")
        content = json.loads(response.content.decode("UTF-8"))

        for item in content["items"]:
            self.assertEqual(
                set(item.keys()),
                {
                    "id",
                    "meta",
                    "title",
                    "width",
                    "height",
                    "media_type",
                    "full_url",
                    "collection",
                },
            )
            self.assertEqual(set(item["meta"].keys()), {"type", "detail_url", "tags"})

    def test_remove_all_meta_fields(self):
        response = self.get_response(fields="-type,-detail_url,-tags,-download_url")
        content = json.loads(response.content.decode("UTF-8"))

        for item in content["items"]:
            self.assertEqual(
                set(item.keys()),
                {
                    "id",
                    "title",
                    "width",
                    "height",
                    "media_type",
                    "full_url",
                    "collection",
                },
            )

    def test_remove_id_field(self):
        response = self.get_response(fields="-id")
        content = json.loads(response.content.decode("UTF-8"))

        for item in content["items"]:
            self.assertEqual(
                set(item.keys()),
                {
                    "meta",
                    "title",
                    "width",
                    "height",
                    "media_type",
                    "full_url",
                    "collection",
                },
            )

    def test_all_fields(self):
        response = self.get_response(fields="*")
        content = json.loads(response.content.decode("UTF-8"))

        for item in content["items"]:
            self.assertEqual(
                set(item.keys()),
                {
                    "id",
                    "meta",
                    "title",
                    "width",
                    "height",
                    "media_type",
                    "collection",
                    "full_url",
                },
            )
            self.assertEqual(
                set(item["meta"].keys()),
                {"type", "detail_url", "tags", "download_url"},
            )

    def test_all_fields_then_remove_something(self):
        response = self.get_response(
            fields="*,-title,-download_url,-media_type,-collection"
        )
        content = json.loads(response.content.decode("UTF-8"))

        for item in content["items"]:
            self.assertEqual(
                set(item.keys()), {"id", "meta", "width", "height", "full_url"}
            )
            self.assertEqual(set(item["meta"].keys()), {"type", "detail_url", "tags"})

    def test_fields_tags(self):
        response = self.get_response(fields="tags")
        content = json.loads(response.content.decode("UTF-8"))

        for item in content["items"]:
            self.assertIsInstance(item["meta"]["tags"], list)

    def test_star_in_wrong_position_gives_error(self):
        response = self.get_response(fields="title,*")
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            content, {"message": "fields error: '*' must be in the first position"}
        )

    def test_fields_which_are_not_in_api_fields_gives_error(self):
        response = self.get_response(fields="uploaded_by_user")
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {"message": "unknown fields: uploaded_by_user"})

    def test_fields_unknown_field_gives_error(self):
        response = self.get_response(fields="123,title,abc")
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {"message": "unknown fields: 123, abc"})

    def test_fields_remove_unknown_field_gives_error(self):
        response = self.get_response(fields="-123,-title,-abc")
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {"message": "unknown fields: 123, abc"})

    def test_filtering_exact_filter(self):
        response = self.get_response(title="2001: A Space Odyssey")
        content = json.loads(response.content.decode("UTF-8"))

        item_id_list = self.get_media_id_list(content)
        self.assertEqual(item_id_list, [self.a_space_odyssey.pk])

    def test_filtering_on_id(self):
        response = self.get_response(id=self.tng.pk)
        content = json.loads(response.content.decode("UTF-8"))

        item_id_list = self.get_media_id_list(content)
        self.assertEqual(item_id_list, [self.tng.pk])

    def test_filtering_tags(self):
        item = Media.objects.last()
        item.tags.add("test")

        response = self.get_response(tags="test")
        content = json.loads(response.content.decode("UTF-8"))

        item_id_list = self.get_media_id_list(content)
        self.assertEqual(item_id_list, [item.pk])

    def test_filtering_unknown_field_gives_error(self):
        response = self.get_response(not_a_field="abc")
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            content,
            {
                "message": "query parameter is not an operation or a recognised field: not_a_field"
            },
        )

    def test_filtering_by_type(self):
        response = self.get_response(type="video")
        content = json.loads(response.content.decode("UTF-8"))

        item_id_list = self.get_media_id_list(content)
        self.assertEqual(item_id_list, [self.a_space_odyssey.pk, self.tng.pk])

        response = self.get_response(type="audio")
        content = json.loads(response.content.decode("UTF-8"))
        item_id_list = self.get_media_id_list(content)
        self.assertEqual(item_id_list, [self.pink_floyd_time.pk])

    def test_ordering_by_title(self):
        response = self.get_response(order="title")
        content = json.loads(response.content.decode("UTF-8"))

        item_id_list = self.get_media_id_list(content)
        self.assertEqual(
            item_id_list,
            [self.a_space_odyssey.pk, self.pink_floyd_time.pk, self.tng.pk],
        )

    def test_ordering_by_title_backwards(self):
        response = self.get_response(order="-title")
        content = json.loads(response.content.decode("UTF-8"))

        item_id_list = self.get_media_id_list(content)
        self.assertEqual(
            item_id_list,
            [self.tng.pk, self.pink_floyd_time.pk, self.a_space_odyssey.pk],
        )

    def test_ordering_by_random(self):
        # add some more items
        for i in range(4):
            create_audio(f"Audio {i}")
            create_video(f"Video {i}")
        content_1 = json.loads(self.get_response().content.decode("UTF-8"))
        item_id_list_1 = self.get_media_id_list(content_1)

        response_2 = self.get_response(order="random")
        content_2 = json.loads(response_2.content.decode("UTF-8"))
        item_id_list_2 = self.get_media_id_list(content_2)

        self.assertNotEqual(item_id_list_1, item_id_list_2)

    def test_ordering_by_random_backwards_gives_error(self):
        response = self.get_response(order="-random")
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(response.status_code, 400)
        if WAGTAIL_VERSION >= (7, 1):
            self.assertEqual(
                content, {"message": "cannot order by '-random' (unknown field)"}
            )
        else:
            self.assertEqual(
                content, {"message": "cannot order by 'random' (unknown field)"}
            )

    def test_ordering_by_random_with_offset_gives_error(self):
        response = self.get_response(order="random", offset=10)
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            content, {"message": "random ordering with offset is not supported"}
        )

    def test_ordering_by_unknown_field_gives_error(self):
        response = self.get_response(order="not_a_field")
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            content, {"message": "cannot order by 'not_a_field' (unknown field)"}
        )

    def test_limit_only_two_items_returned(self):
        response = self.get_response(limit=2)
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(len(content["items"]), 2)

    def test_limit_total_count(self):
        response = self.get_response(limit=2)
        content = json.loads(response.content.decode("UTF-8"))

        # The total count must not be affected by "limit"
        self.assertEqual(content["meta"]["total_count"], Media.objects.count())

    def test_limit_not_integer_gives_error(self):
        response = self.get_response(limit="abc")
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {"message": "limit must be a positive integer"})

    def test_limit_too_high_gives_error(self):
        response = self.get_response(limit=1000)
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {"message": "limit cannot be higher than 20"})

    @override_settings(WAGTAILAPI_LIMIT_MAX=None)
    def test_limit_max_none_gives_no_errors(self):
        response = self.get_response(limit=1000000)
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content["items"]), Media.objects.count())

    @override_settings(WAGTAILAPI_LIMIT_MAX=10)
    def test_limit_maximum_can_be_changed(self):
        response = self.get_response(limit=20)
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {"message": "limit cannot be higher than 10"})

    @override_settings(WAGTAILAPI_LIMIT_MAX=2)
    def test_limit_default_changes_with_max(self):
        # The default limit is 20. If WAGTAILAPI_LIMIT_MAX is less than that,
        # the default should change accordingly.
        response = self.get_response()
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(len(content["items"]), 2)

    def test_offset_3_usually_appears_3rd_in_list(self):
        response = self.get_response()
        content = json.loads(response.content.decode("UTF-8"))
        item_id_list = self.get_media_id_list(content)
        self.assertEqual(item_id_list.index(self.pink_floyd_time.pk), 2)

    def test_offset_3_moves_after_offset(self):
        response = self.get_response(offset=2)
        content = json.loads(response.content.decode("UTF-8"))
        item_id_list = self.get_media_id_list(content)
        self.assertEqual(item_id_list.index(self.pink_floyd_time.pk), 0)

    def test_offset_total_count(self):
        response = self.get_response(offset=10)
        content = json.loads(response.content.decode("UTF-8"))

        # The total count must not be affected by "offset"
        self.assertEqual(content["meta"]["total_count"], Media.objects.count())

    def test_offset_not_integer_gives_error(self):
        response = self.get_response(offset="abc")
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {"message": "offset must be a positive integer"})

    def test_search_for_tng(self):
        response = self.get_response(search="star")
        content = json.loads(response.content.decode("UTF-8"))

        item_id_list = self.get_media_id_list(content)

        self.assertEqual(set(item_id_list), {self.tng.pk})

    def test_search_with_order(self):
        response = self.get_response(search="star", order="title")
        content = json.loads(response.content.decode("UTF-8"))

        item_id_list = self.get_media_id_list(content)

        self.assertEqual(item_id_list, [self.tng.pk])

    @override_settings(WAGTAILAPI_SEARCH_ENABLED=False)
    def test_search_when_disabled_gives_error(self):
        response = self.get_response(search="james")
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {"message": "search is disabled"})

    def test_search_when_filtering_by_tag_gives_error(self):
        response = self.get_response(search="james", tags="wagtail")
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            content,
            {"message": "filtering by tag with a search query is not supported"},
        )


class TestApiMediaDetail(ApiTestBase):
    def get_response(self, media_id, **params):
        return self.client.get(
            reverse("wagtailapi_v2:media:detail", args=(media_id,)), params
        )

    def test_basic(self):
        response = self.get_response(self.a_space_odyssey.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-type"], "application/json")

        # Will crash if the JSON is invalid
        content = json.loads(response.content.decode("UTF-8"))

        # Check the id field
        self.assertIn("id", content)
        self.assertEqual(content["id"], self.a_space_odyssey.pk)

        # Check that the meta section is there
        self.assertIn("meta", content)
        self.assertIsInstance(content["meta"], dict)

        # Check the meta type
        self.assertIn("type", content["meta"])
        self.assertEqual(content["meta"]["type"], "wagtailmedia.Media")

        # Check the meta detail_url
        self.assertIn("detail_url", content["meta"])
        self.assertEqual(content["meta"]["detail_url"], "http://localhost/api/media/1/")

        # Check the meta download_url
        self.assertIn("download_url", content["meta"])
        self.assertEqual(
            content["meta"]["download_url"],
            "/media/media/2001_a_space_odyssey.mp4",
        )

        # Check full_url
        self.assertIn("full_url", content)
        self.assertEqual(
            content["full_url"],
            "http://localhost:8020/media/media/2001_a_space_odyssey.mp4",
        )

        # Check the title field
        self.assertIn("title", content)
        self.assertEqual(content["title"], self.a_space_odyssey.title)

        # Check the tags field
        self.assertIn("tags", content["meta"])
        self.assertEqual(content["meta"]["tags"], [])

    def test_tags(self):
        item = Media.objects.first()
        item.tags.add("hello")
        item.tags.add("world")

        response = self.get_response(item.pk)
        content = json.loads(response.content.decode("UTF-8"))

        self.assertIn("tags", content["meta"])
        self.assertEqual(content["meta"]["tags"], ["hello", "world"])

    @override_settings(WAGTAILAPI_BASE_URL="http://api.example.com/")
    def test_full_url_with_custom_base_url(self):
        response = self.get_response(self.pink_floyd_time.pk)
        content = json.loads(response.content.decode("UTF-8"))

        self.assertIn("full_url", content)
        self.assertEqual(
            content["full_url"],
            "http://localhost:8020/media/media/pink_floyd_time.mp3",
        )

    # FIELDS

    def test_remove_fields(self):
        response = self.get_response(self.tng.pk, fields="-title")
        content = json.loads(response.content.decode("UTF-8"))

        self.assertIn("id", set(content.keys()))
        self.assertNotIn("title", set(content.keys()))

    def test_remove_meta_fields(self):
        response = self.get_response(self.tng.pk, fields="-download_url")
        content = json.loads(response.content.decode("UTF-8"))

        self.assertIn("detail_url", set(content["meta"].keys()))
        self.assertNotIn("download_url", set(content["meta"].keys()))

    def test_remove_id_field(self):
        response = self.get_response(self.tng.pk, fields="-id")
        content = json.loads(response.content.decode("UTF-8"))

        self.assertIn("title", set(content.keys()))
        self.assertNotIn("id", set(content.keys()))

    def test_remove_all_fields(self):
        response = self.get_response(self.tng.pk, fields="_,id,type")
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(set(content.keys()), {"id", "meta"})
        self.assertEqual(set(content["meta"].keys()), {"type"})

    def test_star_in_wrong_position_gives_error(self):
        response = self.get_response(2, fields="title,*")
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            content, {"message": "fields error: '*' must be in the first position"}
        )

    def test_fields_which_are_not_in_api_fields_gives_error(self):
        response = self.get_response(2, fields="path")
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {"message": "unknown fields: path"})

    def test_fields_unknown_field_gives_error(self):
        response = self.get_response(2, fields="123,title,abc")
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {"message": "unknown fields: 123, abc"})

    def test_fields_remove_unknown_field_gives_error(self):
        response = self.get_response(self.tng.pk, fields="-123,-title,-abc")
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {"message": "unknown fields: 123, abc"})

    def test_nested_fields_on_non_relational_field_gives_error(self):
        response = self.get_response(self.tng.pk, fields="title(foo,bar)")
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {"message": "'title' does not support nested fields"})


class TestApiMediaFind(ApiTestBase):
    def get_response(self, **params):
        return self.client.get(reverse("wagtailapi_v2:media:find"), params)

    def test_without_parameters(self):
        response = self.get_response()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response["Content-type"], "application/json")

        # Will crash if the JSON is invalid
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(content, {"message": "not found"})

    def test_find_by_id(self):
        response = self.get_response(id=self.tng.pk)

        self.assertRedirects(
            response,
            "http://localhost"
            + reverse("wagtailapi_v2:media:detail", args=[self.tng.pk]),
            fetch_redirect_response=False,
        )

    def test_find_by_id_nonexistent(self):
        response = self.get_response(id=1234)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response["Content-type"], "application/json")

        # Will crash if the JSON is invalid
        content = json.loads(response.content.decode("UTF-8"))

        self.assertEqual(content, {"message": "not found"})
