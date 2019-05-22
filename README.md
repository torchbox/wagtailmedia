# [wagtailmedia](https://pypi.org/project/wagtailmedia/) [![PyPI](https://img.shields.io/pypi/v/wagtailmedia.svg)](https://pypi.org/project/wagtailmedia/) [![Build Status](https://travis-ci.org/torchbox/wagtailmedia.svg?branch=master)](https://travis-ci.org/torchbox/wagtailmedia)

A module for Wagtail that provides functionality similar to `wagtail.documents` module,
but for audio and video files.

## Compatibility

`wagtailmedia` is compatible with Wagtail 2.2 and above. For compatibility with Wagtail 2.1 and 2.0, use the [v0.2.0 release](https://pypi.org/project/wagtailmedia/0.2.0/).

## How to install

Install using pip:

```sh
pip install wagtailmedia
```

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
from django.utils.html import format_html

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
                    <source src="{0}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
            '''
        else:
            player_code = '''
            <div>
                <audio controls>
                    <source src="{0}" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>
            </div>
            '''

        return format_html(player_code, value.file.url)


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
