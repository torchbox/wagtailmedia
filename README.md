# [wagtailmedia](https://pypi.org/project/wagtailmedia/)

[![PyPI](https://img.shields.io/pypi/v/wagtailmedia.svg)](https://pypi.org/project/wagtailmedia/)
[![PyPI downloads](https://img.shields.io/pypi/dm/wagtailmedia.svg)](https://pypi.org/project/wagtailmedia/)
[![Build Status](https://github.com/torchbox/wagtailmedia/workflows/CI/badge.svg)](https://github.com/torchbox/wagtailmedia/actions)
[![Coverage](https://codecov.io/github/torchbox/wagtailmedia/coverage.svg?branch=master)](https://codecov.io/github/torchbox/wagtailmedia?branch=master)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/torchbox/wagtailmedia/main.svg)](https://results.pre-commit.ci/latest/github/torchbox/wagtailmedia/main)

A module for Wagtail that provides functionality similar to `wagtail.documents` module,
but for audio and video files.

## Install

Install using pip:

```sh
pip install wagtailmedia
```

`wagtailmedia` is compatible with Wagtail 4.1 and above. Check out older releases for compatibility with older versions of Wagtail.

### Settings

In your settings file, add `wagtailmedia` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "wagtailmedia",
    # ...
]
```

All wagtailmedia settings are defined in a single `WAGTAILMEDIA` dictionary in your settings file:

```python
# settings.py

WAGTAILMEDIA = {
    "MEDIA_MODEL": "",  # string, dotted-notation. Defaults to "wagtailmedia.Media"
    "MEDIA_FORM_BASE": "",  # string, dotted-notation. Defaults to an empty string
    "AUDIO_EXTENSIONS": [],  # list of extensions
    "VIDEO_EXTENSIONS": [],  # list of extensions
}
```

`AUDIO_EXTENSIONS` defaults to "aac", "aiff", "flac", "m4a", "m4b", "mp3", "ogg" and "wav".
`VIDEO_EXTENSIONS` defaults to "avi", "h264", "m4v", "mkv", "mov", "mp4", "mpeg", "mpg", "ogv" and "webm".

### URL configuration

Your project needs to be set up to serve user-uploaded files from `MEDIA_ROOT`.
Your Django project may already have this in place, but if not, add the following snippet to `urls.py`:

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... the rest of your URLconf goes here ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

Note that this only works in development mode (`DEBUG = True`);
in production, you will need to configure your web server to serve files from `MEDIA_ROOT`.
For further details, see the Django documentation: [Serving files uploaded by a user during development](https://docs.djangoproject.com/en/stable/howto/static-files/#serving-files-uploaded-by-a-user-during-development)
and [Deploying static files](https://docs.djangoproject.com/en/stable/howto/static-files/deployment/).

With this configuration in place, you are ready to run `./manage.py migrate` to create the database tables used by `wagtailmedia`.

`wagtailmedia` loads additional assets for the chooser panel interface.
Run `./manage.py collectstatic` after the migrations step to collect all the required assets.

### Custom `Media` model

The `Media` model can be customised. To do this, you need
to add a new model to your project that inherits from `wagtailmedia.models.AbstractMedia`.

Then set the `MEDIA_MODEL` attribute in the `WAGTAILMEDIA` settings dictionary to point to it:

```python
# settings.py
WAGTAILMEDIA = {
    "MEDIA_MODEL": "my_app.CustomMedia",
    # ...
}
```

You can customize the model form used with your `Media` model using the `MEDIA_FORM_BASE` setting.
It should be the dotted path to the form and will be used as the base form passed to `modelform_factory()` when constructing the media form.

```python
# settings.py

WAGTAILMEDIA = {
    "MEDIA_FORM_BASE": "my_app.forms.CustomMediaForm",
    # ...
}
```

### Hooks

#### `construct_media_chooser_queryset`

Called when rendering the media chooser view, to allow the media listing QuerySet to be customised.
The callable passed into the hook will receive the current media QuerySet and the request object,
and must return a Media QuerySet (either the original one, or a new one).

```python
from wagtail import hooks


@hooks.register("construct_media_chooser_queryset")
def show_my_uploaded_media_only(media, request):
    # Only show uploaded media
    media = media.filter(uploaded_by_user=request.user)

    return media
```

## How to use

### As a regular Django field

You can use `Media` as a regular Django field. Here’s an example:

```python
from django.db import models

from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel

from wagtailmedia.edit_handlers import MediaChooserPanel


class BlogPageWithMedia(Page):
    author = models.CharField(max_length=255)
    date = models.DateField("Post date")
    body = RichTextField(blank=False)
    featured_media = models.ForeignKey(
        "wagtailmedia.Media",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = Page.content_panels + [
        FieldPanel("author"),
        FieldPanel("date"),
        FieldPanel("body"),
        MediaChooserPanel("featured_media"),
    ]
```

The `MediaChooserPanel` accepts the `media_type` keyword argument (kwarg) to limit the types of media that can be chosen or uploaded.
At the moment only "audio" (`MediaChooserPanel(media_type="audio")`) and "video" (`MediaChooserPanel(media_type="audio")`) are supported,
and any other type will make the chooser behave as if it did not get any kwarg.

#### Name clash with Wagtail

Do not name the field `media`. When rendering the admin UI, Wagtail uses a `media` property for its fields’ CSS & JS assets loading.
Using `media` as a field name breaks the admin UI ([#54](https://github.com/torchbox/wagtailmedia/issues/54)).

### In StreamField

You can use `Media` in StreamField. To do this, you need
to add a new block class that inherits from `wagtailmedia.blocks.AbstractMediaChooserBlock`
and implement your own `render_basic` method.

Here is an example:

```python
from django.db import models
from django.forms.utils import flatatt
from django.utils.html import format_html, format_html_join

from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from wagtailmedia.blocks import AbstractMediaChooserBlock


class TestMediaBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        if not value:
            return ""

        if value.type == "video":
            player_code = """
            <div>
                <video width="{1}" height="{2}" controls>
                    {0}
                    Your browser does not support the video tag.
                </video>
            </div>
            """
        else:
            player_code = """
            <div>
                <audio controls>
                    {0}
                    Your browser does not support the audio element.
                </audio>
            </div>
            """

        return format_html(
            player_code,
            format_html_join(
                "\n", "<source{0}>", [[flatatt(s)] for s in value.sources]
            ),
            value.width,
            value.height,
        )


class BlogPage(Page):
    author = models.CharField(max_length=255)
    date = models.DateField("Post date")
    body = StreamField(
        [
            ("heading", blocks.CharBlock(classname="title", icon="title")),
            ("paragraph", blocks.RichTextBlock(icon="pilcrow")),
            ("media", TestMediaBlock(icon="media")),
        ]
    )

    content_panels = Page.content_panels + [
        FieldPanel("author"),
        FieldPanel("date"),
        FieldPanel("body"),
    ]
```

You can also use audio or video-specific choosers:

```python
# ...
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtailmedia.blocks import AudioChooserBlock, VideoChooserBlock


class BlogPage(Page):
    # ...

    body = StreamField(
        [
            # ... other block definitions
            ("audio", AudioChooserBlock()),
            ("video", VideoChooserBlock()),
        ]
    )
```

### API

To expose media items in the API, you can follow the [Wagtail documentation guide](https://docs.wagtail.org/en/stable/advanced_topics/api/v2/configuration.html#api-v2-configuration)
for API configuration with wagtailmedia specifics:

```python
# api.py
from wagtail.api.v2.router import WagtailAPIRouter
from wagtailmedia.api.views import MediaAPIViewSet


# Register the router
api_router = WagtailAPIRouter("wagtailapi")
# add any other enpoints you need, plus the wagtailmedia one
api_router.register_endpoint("media", MediaAPIViewSet)
```

## Translations

wagtailmedia has translations in French and Chinese. More translations welcome!

## Contributing

All contributions are welcome!

### Install

To make changes to this project, first clone this repository:

```sh
git clone git@github.com:torchbox/wagtailmedia.git
cd wagtailmedia
```

With your preferred virtualenv activated, install testing dependencies:

```sh
pip install -e '.[testing]' -U
```

### pre-commit

Note that this project uses [pre-commit](https://github.com/pre-commit/pre-commit). To set up locally:

```shell
# if you don't have it yet, globally
$ pip install pre-commit
# go to the project directory
$ cd wagtailmedia
# initialize pre-commit
$ pre-commit install

# Optional, run all checks once for this, then the checks will run only on the changed files
$ pre-commit run --all-files
```

### How to run tests

Now you can run tests as shown below:

```sh
tox
```

or, you can run them for a specific environment `tox -e py310-dj41-wagtail41` or specific test
`tox -e py310-dj41-wagtail41 tests.test_views.TestMediaChooserUploadView`

To run the test app interactively, use `tox -e interactive`, visit `http://127.0.0.1:8020/admin/` and log in with `admin`/`changeme`.
