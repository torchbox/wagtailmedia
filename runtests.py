#!/usr/bin/env python

import os
import shutil
import sys
import warnings

from django.core.management import execute_from_command_line

from tests.settings import MEDIA_ROOT, STATIC_ROOT


os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"


def runtests():
    # Don't ignore DeprecationWarnings
    only_wagtailmedia = r"^wagtailmedia(\.|$)"
    warnings.filterwarnings(
        "default", category=DeprecationWarning, module=only_wagtailmedia
    )
    warnings.filterwarnings(
        "default", category=PendingDeprecationWarning, module=only_wagtailmedia
    )

    args = sys.argv[1:]
    argv = sys.argv[:1] + ["test"] + args

    shutil.rmtree(STATIC_ROOT, ignore_errors=True)
    shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    try:
        execute_from_command_line(argv)
    finally:
        shutil.rmtree(STATIC_ROOT, ignore_errors=True)
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)


if __name__ == "__main__":
    runtests()
