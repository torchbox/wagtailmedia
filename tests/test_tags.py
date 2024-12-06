from unittest.mock import patch

from django.test import TestCase

from wagtailmedia.templatetags.media_tags import wagtail_version_gte


class MediaTagsTests(TestCase):
    def test_wagtail_version_gte(self):
        scenarios = [
            ("5.2", "5.2", True),
            ("5.2.1", "5.2", True),
            ("5.2", "5.2.1", False),
            ("4.2", "5.2", False),
        ]

        for wagtail_version, version_to_test, result in scenarios:
            with patch(
                "wagtailmedia.templatetags.media_tags.get_main_version",
                return_value=wagtail_version,
            ):
                self.assertEqual(wagtail_version_gte(version_to_test), result)
