#!/usr/bin/env python

import os
import shutil
import sys
import warnings

from django.core.management import execute_from_command_line

try:
    from wagtail.utils.deprecation import RemovedInWagtail27Warning
except ImportError:
    class RemovedInWagtail27Warning(Warning):
        pass

os.environ['DJANGO_SETTINGS_MODULE'] = 'wagtailmedia.tests.settings'


def runtests():
    # Don't ignore DeprecationWarnings
    only_wagtailmedia = r'^wagtailmedia(\.|$)'
    warnings.filterwarnings('default', category=DeprecationWarning, module=only_wagtailmedia)
    warnings.filterwarnings('default', category=PendingDeprecationWarning, module=only_wagtailmedia)

    args = sys.argv[1:]
    argv = sys.argv[:1] + ['test'] + args
    try:
        # adding an assert to catch RemovedInWagtail27Warning warnings
        warnings.filterwarnings('error', category=RemovedInWagtail27Warning)
        execute_from_command_line(argv)
    finally:
        from wagtailmedia.tests.settings import STATIC_ROOT, MEDIA_ROOT
        shutil.rmtree(STATIC_ROOT, ignore_errors=True)
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)


if __name__ == '__main__':
    runtests()
