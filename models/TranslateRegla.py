#!/usr/bin/env python
# -*- coding: utf-8 -*-
from models.Regla import *

class TranslateRegla(Regla):

    def __init__(self):
        pass
        
    def run(self,content):
        content = self.translate(content)
        return content

    def translate(self,to_translate):
        tabin = u'áéíóúñ'
        tabout = u'aeioun'
        tabin = [ord(char) for char in tabin]
        translate_table = dict(zip(tabin, tabout))
        return to_translate.translate(translate_table).encode('utf-8')
        