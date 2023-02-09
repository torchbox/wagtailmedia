from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django.urls import reverse

from wagtail.admin.panels import FieldPanel, ObjectList
from wagtail.models import Page

from tests.testapp.models import BlogStreamPage
from wagtailmedia.edit_handlers import MediaChooserPanel, MediaFieldComparison
from wagtailmedia.widgets import AdminAudioChooser, AdminMediaChooser, AdminVideoChooser

from .utils import create_audio, create_video


class MediaChooserPanelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.request = RequestFactory().get("/")
        cls.request.user = (
            AnonymousUser()
        )  # technically, Anonymous users cannot access the admin

        cls.audio = create_audio("Test audio", duration=1000)
        cls.video = create_video("Test video", duration=1024)

        # a MediaChooserPanel class that works on BlogStreamPage's 'video' field
        cls.edit_handler = ObjectList([MediaChooserPanel("featured_media")])
        cls.edit_handler = cls.edit_handler.bind_to_model(BlogStreamPage)
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
        cls.media_chooser_panel = cls.my_media_chooser_panel.get_bound_panel(
            instance=cls.test_instance, form=cls.form
        )

    def _init_edit_handler(self, media_type=None):
        my_page_object_list = ObjectList(
            [MediaChooserPanel("featured_media", media_type=media_type)]
        )
        my_page_object_list = my_page_object_list.bind_to_model(BlogStreamPage)

        my_media_chooser_panel = my_page_object_list.children[0]
        form = my_page_object_list.get_form_class()(instance=self.test_instance)
        media_chooser_panel = my_media_chooser_panel.get_bound_panel(
            instance=self.test_instance, form=form, request=self.request
        )

        return form, media_chooser_panel

    def test_panel_definition(self):
        self.assertIsInstance(self.my_media_chooser_panel, FieldPanel)
        self.assertEqual(
            self.my_media_chooser_panel.get_form_options()["widgets"],
            {"featured_media": AdminMediaChooser},
        )

        for media_type, widget_class in {
            "audio": AdminAudioChooser,
            "video": AdminVideoChooser,
        }.items():
            with self.subTest(msg=f"Testing widget overrides with {media_type}"):
                panel = MediaChooserPanel("fake_media_field", media_type=media_type)
                self.assertEqual(panel._widget_class, widget_class)

    def test_media_chooser_uses_correct_widget(self):
        self.assertEqual(
            type(self.form.fields["featured_media"].widget), AdminMediaChooser
        )

        form, media_chooser_panel = self._init_edit_handler(media_type="audio")
        self.assertEqual(type(form.fields["featured_media"].widget), AdminAudioChooser)

        form, media_chooser_panel = self._init_edit_handler(media_type="video")
        self.assertEqual(type(form.fields["featured_media"].widget), AdminVideoChooser)

    def test_render_js_init(self):
        self.assertIn(
            'createMediaChooser("id_featured_media");',
            self.media_chooser_panel.render_as_field(),
        )

    def test_render_js_init_with_media_type(self):
        # construct an alternative page chooser panel object, with can_choose_root=True

        form, media_chooser_panel = self._init_edit_handler(media_type="audio")
        self.assertIn(
            'createMediaChooser("id_featured_media")',
            media_chooser_panel.render_as_field(),
        )

    def test_get_chosen_item(self):
        self.assertEqual(
            self.media_chooser_panel.bound_field.form.initial["featured_media"],
            self.video.pk,
        )

    def test_render_as_field(self):
        result = self.media_chooser_panel.render_as_field()

        chooser_url = reverse("wagtailmedia:chooser")
        self.assertIn(f'data-chooser-url="{chooser_url}"', result)
        self.assertIn('<span class="title">Test video</span>', result)
        edit_url = reverse("wagtailmedia:edit", args=(self.video.pk,))
        self.assertIn(
            f'<a href="{edit_url}" aria-describedby="id_featured_media-title" '
            f'class="edit-link button button-small button-secondary" '
            f'target="_blank" rel="noreferrer">Edit this media item</a>',
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
        self.assertIn(
            f'<a href="{edit_url}" aria-describedby="id_featured_media-title" '
            f'class="edit-link button button-small button-secondary" '
            f'target="_blank" rel="noreferrer">Edit this video</a>',
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

        self.assertIn(
            '<a href="" aria-describedby="id_featured_media-title" '
            'class="edit-link button button-small button-secondary w-hidden" target="_blank" '
            'rel="noreferrer">Edit this media item</a>',
            result,
        )
        self.assertIn("Choose a media item", result)

    def test_render_error(self):
        form = self.MediaChooserForm(
            {"featured_media": ""}, instance=self.test_instance
        )
        self.assertFalse(form.is_valid())

        media_chooser_panel = self.my_media_chooser_panel.get_bound_panel(
            instance=self.test_instance, form=form, request=self.request
        )

        self.assertInHTML(
            '<p class="error-message">This field is required.</p>',
            media_chooser_panel.render_as_field(),
        )

    def test_comparison_class(self):
        self.assertIs(
            self.my_media_chooser_panel.get_comparison_class(), MediaFieldComparison
        )
