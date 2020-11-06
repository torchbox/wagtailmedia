#!/usr/bin/env python

import io

from wagtailmedia import __version__


try:
    from setuptools import find_packages, setup
except ImportError:
    from distutils.core import setup


# Testing dependencies
testing_extras = [
    # Required for running the tests
    "mock>=1.0.0",
    # For coverage and PEP8 linting
    "coverage>=3.7.0",
    "flake8>=3.6.0",
    "isort==5.6.4",  # leave this pinned - it tends to change rules between patch releases
    # Required for running tests in Vagrant
    "tox==3.9.0",
    # Required for interactive testing via tox
    "psycopg2-binary",
    "django-redis-cache",
]

with io.open("README.md", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name="wagtailmedia",
    version=__version__,
    description="A module for Wagtail that provides functionality "
    "similar to wagtail.documents module, but for audio and video files.",
    author="Mikalai Radchuk",
    author_email="mikalai.radchuk@torchbox.com",
    url="https://github.com/torchbox/wagtailmedia",
    packages=find_packages(),
    include_package_data=True,
    license="BSD",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Framework :: Django",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Wagtail :: 2",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
    ],
    install_requires=[
        "wagtail>=2.7",
    ],
    extras_require={
        "testing": testing_extras,
    },
    zip_safe=False,
)
