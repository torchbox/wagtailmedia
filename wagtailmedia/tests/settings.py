import os

from wagtail import VERSION as WAGTAIL_VERSION


DEBUG = "INTERACTIVE" in os.environ

WAGTAILMEDIA_ROOT = os.path.dirname(__file__)
STATIC_ROOT = os.path.join(WAGTAILMEDIA_ROOT, "test-static")
MEDIA_ROOT = os.path.join(WAGTAILMEDIA_ROOT, "test-media")
MEDIA_URL = "/media/"

POSTGRES_PORT = os.getenv("POSTGRES_5432_TCP_PORT", "")
if POSTGRES_PORT:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "pgdb",
            "USER": "pguser",
            "PASSWORD": "pgpass",
            "HOST": "localhost",
            "PORT": POSTGRES_PORT,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": os.environ.get("DATABASE_ENGINE", "django.db.backends.sqlite3"),
            "NAME": os.environ.get("DATABASE_NAME", "db.sqlite3"),
            "USER": os.environ.get("DATABASE_USER", None),
            "PASSWORD": os.environ.get("DATABASE_PASS", None),
            "HOST": os.environ.get("DATABASE_HOST", None),
            "TEST": {
                "NAME": os.environ.get("DATABASE_NAME", None),
            },
        }
    }


SECRET_KEY = "not needed"

ROOT_URLCONF = "wagtailmedia.tests.urls"

STATIC_URL = "/static/"
STATIC_ROOT = STATIC_ROOT

STATICFILES_FINDERS = ("django.contrib.staticfiles.finders.AppDirectoriesFinder",)

USE_TZ = True

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
                "wagtail.contrib.settings.context_processors.settings",
            ],
            "debug": True,
        },
    }
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if WAGTAIL_VERSION < (2, 9):
    MIDDLEWARE += ["wagtail.core.middleware.SiteMiddleware"]

MIDDLEWARE += [
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

INSTALLED_APPS = [
    "wagtailmedia.tests.testapp",
    "wagtailmedia",
    "taggit",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "wagtail.contrib.redirects",
    "wagtail.images",
    "wagtail.users",
    "wagtail.documents",
    "wagtail.admin",
    "wagtail.core",
]


# Using DatabaseCache to make sure THAT the cache is cleared between tests.
# This prevents false-positives in some wagtail core tests where we are
# changing the 'wagtail_root_paths' key which may cause future tests to fail.

REDIS_PORT = os.getenv("REDIS_6379_TCP_PORT", "")

if REDIS_PORT:
    CACHES = {
        "default": {
            "BACKEND": "redis_cache.RedisCache",
            "LOCATION": "localhost:%s" % REDIS_PORT,
        },
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "cache",
        }
    }

PASSWORD_HASHERS = (
    "django.contrib.auth.hashers.MD5PasswordHasher",  # don't use the intentionally slow default password hasher
)


WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.db",
    }
}

# must be set for interactive demo, copied per
# https://github.com/django/django/commit/adb96617897690b3a01e39e8297ae7d67825d2bc
ALLOWED_HOSTS = "*"

WAGTAIL_SITE_NAME = "Test Site"
