#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

required = open('requirements.txt').read().split('\n')[:-1]

setup(
    name='heroku',
    version='0.2.0',
    description='Heroku API Wrapper.',
    long_description=(open('README.rst').read() + '\n\n' +
                      open('HISTORY.rst').read()),
    author='Felipe Rodrigues',
    author_email='felipe@felipevr.com',
    url='https://github.com/fbidu/pyheroku',
    packages=['heroku'],
    package_data={'': ['LICENSE']},
    include_package_data=True,
    install_requires=required,
    license='MIT',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)
