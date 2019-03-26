#!/usr/bin/env python

from wagtailmedia import __version__

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


# Testing dependencies
testing_extras = [
    # Required for running the tests
    'mock>=1.0.0',

    # For coverage and PEP8 linting
    'coverage>=3.7.0',
    'flake8>=2.2.0',
]

setup(
    name='wagtailmedia',
    version=__version__,
    description='A module for Wagtail that provides functionality '
                'similar to wagtail.wagtaildocs module, but for audio and video files.',
    author='Mikalai Radchuk',
    author_email='mikalai.radchuk@torchbox.com',
    url='https://github.com/torchbox/wagtailmedia',
    packages=find_packages(),
    include_package_data=True,
    license='BSD',
    long_description='See https://github.com/torchbox/wagtailmedia for details',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
    install_requires=[
        'wagtail>=2.2',
    ],
    extras_require={
        'testing': testing_extras,
    },
    zip_safe=False,
)
