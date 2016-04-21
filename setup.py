#!/usr/bin/env python

from wagtailmedia import __version__

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


setup(
    name='wagtailmedia',
    version=__version__,
    description='A module for Wagtail that provides functionality '
                'similar to wagtail.wagtaildocs module, but for audio and video files.',
    author='Mikalai Radchuk',
    author_email='mikalai.radchuk@torchbox.com',
    packages=find_packages(),
    include_package_data=True,
    license='BSD',
    long_description=open('README.rst').read(),
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
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
    install_requires=[
        'Django>=1.8.1,<1.10',
        'wagtail>=1.4',
    ],
    zip_safe=False,
)
