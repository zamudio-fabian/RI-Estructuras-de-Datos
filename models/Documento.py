#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Documento:

    filename = ''
    content = ''
    tamanio = 0
    tokens = []
    terminos = {}

    def __init__(self,filename,content):
        self.filename = filename
        self.content = content
        self.tamanio = len(content)