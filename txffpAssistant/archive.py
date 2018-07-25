#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : Kyle
# @License : MIT
# @Contact : kairu_madigan@yahoo.co.jp
# @Date    : 2018/07/24 23:54

import io
import os
import sys
import tempfile
import zipfile

import filetype


def is_zip(obj):
    kind = filetype.archive(obj)
    if kind.extension == "zip":
        return True
    return False
