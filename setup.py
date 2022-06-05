#!/usr/bin/env python

import io

from setuptools import find_packages, setup


# Testing dependencies
testing_extras = [
    # Required for running the tests
    "mock>=1.0.0",
    # For coverage and PEP8 linting
    "coverage>=3.7.0",
    "tox~=3.24",
]

version = {}
with io.open("src/wagtailmedia/version.py") as fp:
    exec(fp.read(), version)

with io.open("README.md", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name="wagtailmedia",
    version=version["__version__"],
    description="A module for Wagtail that provides functionality "
    "similar to wagtail.documents module, but for audio and video files.",
    author="Mikalai Radchuk",
    author_email="hello@torchbox.com",
    maintainer="Dan Braghis",
    maintainer_email="dan.braghis@torchbox.com",
    project_urls={
        "Changelog": "https://github.com/torchbox/wagtailmedia/blob/main/CHANGELOG.md",
    },
    url="https://github.com/torchbox/wagtailmedia",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    license="BSD",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["wagtail", "django", "media"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.2",
        "Framework :: Wagtail",
        "Framework :: Wagtail :: 2",
        "Framework :: Wagtail :: 3",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
    ],
    install_requires=[
        "wagtail>=2.15",
    ],
    extras_require={
        "testing": testing_extras,
    },
    zip_safe=False,
)
