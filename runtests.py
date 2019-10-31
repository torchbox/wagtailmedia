#!/usr/bin/env python

import os
import shutil
import sys
import warnings

from django.core.management import execute_from_command_line
from wagtail.utils.deprecation import RemovedInWagtail27Warning

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
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            execute_from_command_line(argv)
            for warning in w:
                assert not isinstance(warning.message, RemovedInWagtail27Warning), \
                    'These tests raised a RemovedInWagtail27Warning.'
    finally:
        from wagtailmedia.tests.settings import STATIC_ROOT, MEDIA_ROOT
        shutil.rmtree(STATIC_ROOT, ignore_errors=True)
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)


if __name__ == '__main__':
    runtests()
