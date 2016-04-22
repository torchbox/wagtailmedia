============
wagtailmedia
============

A module for Wagtail that provides functionality similar to ``wagtail.wagtaildocs`` module,
but for audio and video files.


How to install
==============

Install using pip::

    pip install git+https://github.com/torchbox/wagtailmedia.git


Settings
--------

In your settings file, add ``wagtailmedia`` to ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'wagtailmedia',
        # ...
    ]


URL configuration
-----------------

Now make the following additions to your ``urls.py`` file:

.. code-block:: python

    from wagtailmedia import urls as wagtailmedia_urls

    urlpatterns = [
        # ...
        url(r'^media_files/', include(wagtailmedia_urls)),
        # ...
    ]


Finally, your project needs to be set up to serve user-uploaded files from ``MEDIA_ROOT``.
Your Django project may already have this in place, but if not, add the following snippet to ``urls.py``:

.. code-block:: python

    from django.conf import settings
    from django.conf.urls.static import static

    urlpatterns = [
        # ... the rest of your URLconf goes here ...
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


Note that this only works in development mode (``DEBUG = True``);
in production, you will need to configure your web server to serve files from ``MEDIA_ROOT``.
For further details, see the Django documentation: `Serving files uploaded by a user during development <https://docs.djangoproject.com/en/stable/howto/static-files/#serving-files-uploaded-by-a-user-during-development>`_
and `Deploying static files <https://docs.djangoproject.com/en/stable/howto/static-files/deployment/>`_.

With this configuration in place, you are ready to run ``./manage.py migrate`` to create the database tables used by wagtailmedia.


Custom ``Media`` model
----------------------

The ``Media`` model can be customised. To do this, you need
to add a new model to your project that inherits from ``wagtailmedia.models.AbstractMedia``.

Then set the ``WAGTAILMEDIA_MEDIA_MODEL`` setting to point to it:

.. code-block:: python

    WAGTAILMEDIA_MEDIA_MODEL = 'mymedia.CustomMedia'


How to use
==========

You can use ``Media`` in StreamField. To do this, you need
to add a new block class that inherits from ``wagtailmedia.blocks.AbstractMediaChooserBlock``
and implement your own ``render_basic`` method.

Here is an example:

.. code-block:: python

    from __future__ import unicode_literals
    from django.utils.html import format_html
    from wagtailmedia.blocks import AbstractMediaChooserBlock

    class TestMediaBlock(AbstractMediaChooserBlock):
        def render_basic(self, value):
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

You also can use your template engine. For more detail see `StreamField documentation <http://docs.wagtail.io/en/stable/topics/streamfield.html#basic-block-types>`_.
