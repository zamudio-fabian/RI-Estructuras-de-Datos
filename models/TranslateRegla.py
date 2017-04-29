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
        tabin = [u'áéíóúñ', u'àèìòùñ', u'äëïöüñ', u'âêîôûñ']
        tabout = u'aeioun'
        translate_table = {}
        for i in xrange(0, len(tabin)):
            translate_table.update(dict(zip([ord(char) for char in tabin[i]], tabout)))
        return to_translate.translate(translate_table)
        