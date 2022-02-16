from django.contrib.auth.models import AnonymousUser
from django.core.files.base import ContentFile
from django.test import RequestFactory, TestCase
from django.urls import reverse

from wagtail import VERSION as WAGTAIL_VERSION
from wagtail.admin.edit_handlers import ObjectList
from wagtail.core.models import Page

from tests.testapp.models import BlogStreamPage
from wagtailmedia.edit_handlers import MediaChooserPanel
from wagtailmedia.models import Media
from wagtailmedia.widgets import AdminAudioChooser, AdminMediaChooser, AdminVideoChooser


class MediaChooserPanelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.request = RequestFactory().get("/")
        cls.request.user = (
            AnonymousUser()
        )  # technically, Anonymous users cannot access the admin

        fake_file = ContentFile("Test")
        fake_file.name = "test.mp3"

        cls.audio = Media.objects.create(
            title="Test audio", duration=1000, file=fake_file, type="audio"
        )

        fake_file = ContentFile("Test")
        fake_file.name = "test.mp4"

        cls.video = Media.objects.create(
            title="Test video", duration=1024, file=fake_file, type="video"
        )

        # a MediaChooserPanel class that works on BlogStreamPage's 'video' field
        cls.edit_handler = ObjectList([MediaChooserPanel("featured_media")]).bind_to(
            model=BlogStreamPage, request=cls.request
        )
        cls.my_media_chooser_panel = cls.edit_handler.children[0]

        # build a form class containing the fields that MyPageChooserPanel wants
        cls.MediaChooserForm = cls.edit_handler.get_form_class()

        root_page = Page.objects.first()
        cls.test_instance = BlogStreamPage(
            title="Post",
            slug="post",
            author="Joe Bloggs",
            date="1984-01-01",
            featured_media=cls.video,
        )
        root_page.add_child(instance=cls.test_instance)

        cls.form = cls.MediaChooserForm(instance=cls.test_instance)
        cls.media_chooser_panel = cls.my_media_chooser_panel.bind_to(
            instance=cls.test_instance, form=cls.form
        )

    def test_media_chooser_uses_correct_widget(self):
        self.assertEqual(
            type(self.form.fields["featured_media"].widget), AdminMediaChooser
        )

        form, media_chooser_panel = self._init_edit_handler(media_type="audio")
        self.assertEqual(type(form.fields["featured_media"].widget), AdminAudioChooser)

        form, media_chooser_panel = self._init_edit_handler(media_type="video")
        self.assertEqual(type(form.fields["featured_media"].widget), AdminVideoChooser)

    def test_render_js_init(self):
        result = self.media_chooser_panel.render_as_field()
        self.assertIn('createMediaChooser("id_featured_media");', result)

    def test_render_js_init_with_media_type(self):
        # construct an alternative page chooser panel object, with can_choose_root=True

        form, media_chooser_panel = self._init_edit_handler(media_type="audio")
        result = media_chooser_panel.render_as_field()

        self.assertIn('createMediaChooser("id_featured_media")', result)

    def _init_edit_handler(self, media_type=None):
        my_page_object_list = ObjectList(
            [MediaChooserPanel("featured_media", media_type=media_type)]
        ).bind_to(model=BlogStreamPage)
        my_media_chooser_panel = my_page_object_list.children[0]
        form = my_page_object_list.get_form_class()(instance=self.test_instance)
        media_chooser_panel = my_media_chooser_panel.bind_to(
            instance=self.test_instance, form=form, request=self.request
        )
        return form, media_chooser_panel

    def test_get_chosen_item(self):
        result = self.media_chooser_panel.get_chosen_item()
        self.assertEqual(result, self.video)

    def test_render_as_field(self):
        result = self.media_chooser_panel.render_as_field()

        chooser_url = reverse("wagtailmedia:chooser")
        self.assertIn(f'data-chooser-url="{chooser_url}"', result)
        self.assertIn('<span class="title">Test video</span>', result)
        edit_url = reverse("wagtailmedia:edit", args=(self.video.pk,))
        if WAGTAIL_VERSION >= (2, 17):
            self.assertIn(
                f'<a href="{edit_url}" class="edit-link button button-small button-secondary" '
                f'target="_blank" rel="noreferrer">Edit this media item</a>',
                result,
            )
        else:
            self.assertIn(
                f'<a href="{edit_url}" class="edit-link button button-small button-secondary" '
                f'target="_blank" rel="noopener noreferrer">Edit this media item</a>',
                result,
            )
        self.assertIn("Choose a media item", result)

    def test_render_as_field_with_media_type(self):
        form, media_chooser_panel = self._init_edit_handler(media_type="video")
        result = media_chooser_panel.render_as_field()

        chooser_url = reverse("wagtailmedia:chooser_typed", args=("video",))
        self.assertIn(f'data-chooser-url="{chooser_url}"', result)
        self.assertIn('<span class="title">Test video</span>', result)
        edit_url = reverse("wagtailmedia:edit", args=(self.video.pk,))
        if WAGTAIL_VERSION >= (2, 17):
            self.assertIn(
                f'<a href="{edit_url}" class="edit-link button button-small button-secondary" '
                f'target="_blank" rel="noreferrer">Edit this video</a>',
                result,
            )
        else:
            self.assertIn(
                f'<a href="{edit_url}" class="edit-link button button-small button-secondary" '
                f'target="_blank" rel="noopener noreferrer">Edit this video</a>',
                result,
            )
        self.assertIn("Choose video", result)

    def test_render_as_empty_field(self):
        test_instance = BlogStreamPage()
        form = self.MediaChooserForm(instance=test_instance)
        media_chooser_panel = self.my_media_chooser_panel.bind_to(
            instance=test_instance, form=form, request=self.request
        )
        result = media_chooser_panel.render_as_field()

        self.assertIn('<span class="title"></span>', result)

        if WAGTAIL_VERSION >= (2, 17):
            self.assertIn(
                '<a href="" class="edit-link button button-small button-secondary" target="_blank" '
                'rel="noreferrer">Edit this media item</a>',
                result,
            )
        else:
            self.assertIn(
                '<a href="" class="edit-link button button-small button-secondary" target="_blank" '
                'rel="noopener noreferrer">Edit this media item</a>',
                result,
            )
        self.assertIn("Choose a media item", result)

    def test_render_error(self):
        form = self.MediaChooserForm(
            {"featured_media": ""}, instance=self.test_instance
        )
        self.assertFalse(form.is_valid())

        media_chooser_panel = self.my_media_chooser_panel.bind_to(
            instance=self.test_instance, form=form, request=self.request
        )
        self.assertIn(
            "<span>This field is required.</span>",
            media_chooser_panel.render_as_field(),
        )
