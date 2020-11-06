# [wagtailmedia](https://pypi.org/project/wagtailmedia/) [![PyPI](https://img.shields.io/pypi/v/wagtailmedia.svg)](https://pypi.org/project/wagtailmedia/)  [![PyPI downloads](https://img.shields.io/pypi/dm/wagtailmedia.svg)](https://pypi.org/project/wagtailmedia/) [![Build Status](https://travis-ci.org/torchbox/wagtailmedia.svg?branch=master)](https://travis-ci.org/torchbox/wagtailmedia) [![Coverage](https://codecov.io/github/torchbox/wagtailmedia/coverage.svg?branch=master)](https://codecov.io/github/torchbox/wagtailmedia?branch=master)

A module for Wagtail that provides functionality similar to `wagtail.documents` module,
but for audio and video files.

## Install

Install using pip:

```sh
pip install wagtailmedia
```

`wagtailmedia` is compatible with Wagtail 2.7 and above. Check out older releases for compatibility with older versions of Wagtail.

### Settings

In your settings file, add `wagtailmedia` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'wagtailmedia',
    # ...
]
```

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

With this configuration in place, you are ready to run `./manage.py migrate` to create the database tables used by wagtailmedia.

### Custom `Media` model

The `Media` model can be customised. To do this, you need
to add a new model to your project that inherits from `wagtailmedia.models.AbstractMedia`.

Then set the `WAGTAILMEDIA_MEDIA_MODEL` setting to point to it:

```python
WAGTAILMEDIA_MEDIA_MODEL = 'mymedia.CustomMedia'
```

You can customize the model form used with your `Media` model using the `WAGTAILMEDIA_MEDIA_FORM_BASE` setting.  It should be the dotted path to the form and will be used as the base form passed to modelform_factory() when constructing the media form.

### Hooks

#### `construct_media_chooser_queryset`

Called when rendering the media chooser view, to allow the media listing QuerySet to be customised.
The callable passed into the hook will receive the current media QuerySet and the request object, and must return a Media QuerySet (either the original one, or a new one).

```python
from wagtail.core import hooks

@hooks.register('construct_media_chooser_queryset')
def show_my_uploaded_media_only(media, request):
    # Only show uploaded media
    media = media.filter(uploaded_by_user=request.user)

    return media
```

## How to use

### As a regular Django field

You can use `Media` as a regular Django field. Here’s an example:

```python
from __future__ import unicode_literals

from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel

from wagtailmedia.edit_handlers import MediaChooserPanel


class BlogPageWithMedia(Page):
    author = models.CharField(max_length=255)
    date = models.DateField("Post date")
    body = RichTextField(blank=False)
    featured_media = models.ForeignKey(
        'wagtailmedia.Media',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('author'),
        FieldPanel('date'),
        FieldPanel('body'),
        MediaChooserPanel('featured_media'),
    ]
```

#### Name clash with Wagtail

Do not name the field `media`. When rendering the admin UI, Wagtail uses a `media` property for its fields’ CSS & JS assets loading. Using `media` as a field name breaks the admin UI ([#54](https://github.com/torchbox/wagtailmedia/issues/54)).

### In StreamField

You can use `Media` in StreamField. To do this, you need
to add a new block class that inherits from `wagtailmedia.blocks.AbstractMediaChooserBlock`
and implement your own `render_basic` method.

Here is an example:

```python
from __future__ import unicode_literals

from django.db import models
from django.forms.utils import flatatt
from django.utils.html import format_html, format_html_join

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore import blocks
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel

from wagtailmedia.blocks import AbstractMediaChooserBlock


class TestMediaBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        if not value:
            return ''

        if value.type == 'video':
            player_code = '''
            <div>
                <video width="320" height="240" controls>
                    {0}
                    Your browser does not support the video tag.
                </video>
            </div>
            '''
        else:
            player_code = '''
            <div>
                <audio controls>
                    {0}
                    Your browser does not support the audio element.
                </audio>
            </div>
            '''

        return format_html(player_code, format_html_join(
            '\n', "<source{0}>",
            [[flatatt(s)] for s in value.sources]
        ))


class BlogPage(Page):
    author = models.CharField(max_length=255)
    date = models.DateField("Post date")
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title", icon='title')),
        ('paragraph', blocks.RichTextBlock(icon='pilcrow')),
        ('media', TestMediaBlock(icon='media')),
    ])

    content_panels = Page.content_panels + [
        FieldPanel('author'),
        FieldPanel('date'),
        StreamFieldPanel('body'),
    ]
```

## Translations

wagtailmedia has translations in French and Chinese. More translations welcome!

## Contributing

### Install

To make changes to this project, first clone this repository:

```sh
git clone git@github.com:torchbox/wagtailmedia.git
cd wagtailmedia
```

With your preferred virtualenv activated, install testing dependencies:

```sh
pip install -e .[testing] -U
```

### How to run tests

Now you can run tests as shown below:

```sh
python runtests.py
```

Alternately, you can skip local configuration and use the provided vagrant environment for testing.
[Reference its README for further details.](vagrant/README)
