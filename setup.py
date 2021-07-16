#!/usr/bin/env python
#
# texttable - module for creating simple ASCII tables
# Copyright (C) 2003-2020 Gerome Fournier <jef(at)foutaise.org>

from setuptools import setup, find_packages
import os
from os.path import dirname

DESCRIPTION = "module for creating simple colorful formatted ASCII tables"
HERE = dirname(__file__)

with open("README.md") as f:
    LONG_DESCRIPTION = f.read()

# def _get_install_requires(fname):
#     result = [req_line.strip() for req_line in open(fname)
#               if req_line.strip() and not req_line.startswith('#')]

#     return result

setup(
    name="blessedtable",
    version="1.0.0",
    author="Shuvo Kumar Paul",
    author_email="shuvo.k.paul@gmail.com",
    url="https://github.com/paul-shuvo/blessedtable",
    download_url="https://github.com/paul-shuvo/blessedtable/archive/refs/tags/v1.0.0.zip",
    license="MIT",
    install_requires=[
            "blessed",
            "texttable==1.6.4"
        ],
    py_modules=["blessedtable"],
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    platforms="any",
    package_dir={"": "blessedtable"},
    packages=find_packages(where="blessedtable"),
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing',
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    options={"bdist_wheel": {"universal": "1"}},
    keywords=['terminal', 'sequences', 'tty', 'curses', 'ncurses',
            'formatting', 'style', 'color', 'console', 'keyboard',
            'ansi', 'xterm', 'table', 'ascii'],
)
