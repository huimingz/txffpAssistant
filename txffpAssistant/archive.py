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


def get_zipfile(filepath):
    if os.path.isdir(filepath):
        for root, dirs, files in os.walk(filepath):
            for fn in files:
                fp = os.path.join(root, fn)
                if is_zip(fp):
                    yield fp
    
    elif os.path.isfile(filepath):
        if is_zip(filepath):
            yield filepath
        else:
            return iter([])
