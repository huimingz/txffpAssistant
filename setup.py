#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : Kyle
# @License : MIT
# @Contact : kairu_madigan@yahoo.co.jp
# @Date    : 2018/07/23 14:24
import io
import re
import sys

from setuptools import setup, find_packages


if sys.version_info < (3, 5):
    sys.exit("Sorry, Python < 3.5 is not supported")

with io.open("README.md", "rt", encoding="utf8") as f:
    readme = f.read()

with io.open("txffpAssistant/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = \"(.*?)\"', f.read()).group(1)

setup(
    name="txffpAssistant",
    version=version,
    packages=find_packages(),
    url="",
    license="MIT",
    author="Kyle",
    author_email="kairu_madigan@yahoo.co.jp",
    description="",
    long_description=readme,
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    python_requires=">=3.5",
    install_requires=[
        "lxml>=4.2.3",
        "requests>=2.19.1",
        "PyPDF2>=1.26.0",
        "filetype>=1.0.1"
    ],
    classifiers=[
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Chinese (Simplified)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ],
    entry_points={
        "console_scripts": [
            "txffp = txffpAssistant.cli:main",
        ]
    }
)
