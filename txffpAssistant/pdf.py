#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : Kyle
# @License : MIT
# @Contact : kairu_madigan@yahoo.co.jp
# @Date    : 2018/07/25 14:53

import tempfile

from PyPDF2 import PdfFileWriter, PdfFileReader


class PDFMerger(object):
    
    def __init__(self):
        self._pdf_writer = PdfFileWriter()
    
    def add_pdf(self, stream):
        """
        Args:
            stream: A File object or an object that supports the standard
            read and seek methods similar to a File object. Could also be
            a string representing a path to a PDF file.
        """
        pdf_reader = PdfFileReader(stream)
        for page_num in range(pdf_reader.getNumPages()):
            self._pdf_writer.addPage(pdf_reader.getPage(page_num))
            
    def write(self, stream):
        """
        Args:
            stream: An object to write the file to. The object must support
            the write method and the tell method, similar to a file object.
        """
        self._pdf_writer.write(stream)
