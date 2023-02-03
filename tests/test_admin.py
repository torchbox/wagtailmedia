from django.test import TestCase
from django.urls import reverse

from wagtail import VERSION as WAGTAIL_VERSION


if WAGTAIL_VERSION >= (3, 0):
    from wagtail.models import Page
    from wagtail.test.utils import WagtailTestUtils
else:
    from wagtail.core.models import Page
    from wagtail.tests.utils import WagtailTestUtils

from wagtailmedia.blocks import AbstractMediaChooserBlock


class TestMediaBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        return None


class TestAdminInterface(TestCase, WagtailTestUtils):
    def setUp(self):
        self.user = self.login()
        self.root_page = Page.objects.first()

    def test_media_field_in_admin(self):
        """
        EventPage does not trigger telepath to be loaded, but media-chooser
        should be included.
        """
        response = self.client.get(
            reverse(
                "wagtailadmin_pages:add",
                args=("wagtailmedia_tests", "eventpage", self.root_page.id),
            )
        )
        self.assertContains(
            response,
            '<script>createMediaChooser("id_related_media-__prefix__-link_media");<-/script>',
        )
        self.assertContains(response, "media-chooser.js")

    def test_media_block_in_admin(self):
        response = self.client.get(
            reverse(
                "wagtailadmin_pages:add",
                args=("wagtailmedia_tests", "blogstreampage", self.root_page.id),
            )
        )
        self.assertContains(
            response, "media-chooser.js"
        )  # blogstreampage != eventpage -> test again
        # media chooser form is rendered from json by telepath
        self.assertContains(response, "media-chooser-telepath.js")
        self.assertContains(response, "wagtailmedia.MediaChooser")
        # assert media chooser form is included in json encoded form
        self.assertContains(
            response, "class=\\&quot;chooser media-chooser blank\\&quot;"
        )
