#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Documento:

    def __init__(self,id,filename,content):
        self.id = id
        self.filename = filename
        self.content = content
        self.tamanio = len(content)