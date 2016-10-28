import os

WAGTAILMEDIA_ROOT = os.path.dirname(__file__)
STATIC_ROOT = os.path.join(WAGTAILMEDIA_ROOT, 'test-static')
MEDIA_ROOT = os.path.join(WAGTAILMEDIA_ROOT, 'test-media')
MEDIA_URL = '/media/'

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DATABASE_NAME', 'wagtailmedia'),
        'USER': os.environ.get('DATABASE_USER', None),
        'PASSWORD': os.environ.get('DATABASE_PASS', None),
        'HOST': os.environ.get('DATABASE_HOST', None),

        'TEST': {
            'NAME': os.environ.get('DATABASE_NAME', None),
        }
    }
}


SECRET_KEY = 'not needed'

ROOT_URLCONF = 'wagtailmedia.tests.urls'

STATIC_URL = '/static/'
STATIC_ROOT = STATIC_ROOT

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

USE_TZ = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'wagtail.contrib.settings.context_processors.settings',
            ],
            'debug': True,
        },
    }
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'wagtail.wagtailcore.middleware.SiteMiddleware',
    'wagtail.wagtailredirects.middleware.RedirectMiddleware',
)

INSTALLED_APPS = (
    'wagtailmedia.tests.testapp',
    'wagtailmedia',

    'wagtail.wagtailredirects',
    'wagtail.wagtailimages',
    'wagtail.wagtailusers',
    'wagtail.wagtaildocs',
    'wagtail.wagtailadmin',
    'wagtail.wagtailcore',

    'taggit',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
)


# Using DatabaseCache to make sure THAT the cache is cleared between tests.
# This prevents false-positives in some wagtail core tests where we are
# changing the 'wagtail_root_paths' key which may cause future tests to fail.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache',
    }
}

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',  # don't use the intentionally slow default password hasher
)


WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.wagtailsearch.backends.db',
    }
}


WAGTAIL_SITE_NAME = "Test Site"
