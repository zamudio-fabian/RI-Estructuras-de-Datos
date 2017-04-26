#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from models.Regla import *

class TelefonosRegla(Regla):

    regex = None
    filename = 'results/telefonos.txt'

    def __init__(self):
        self.regex = re.compile(u"(?<=\s|:)\(?(?:(0?[1-3]\d{1,2})\)?(?:\s|-)?)?((?:\d[\d-]{5}|15[\s\d-]{7})\d+)|\+\d{2,2}\d{9,11}")
        
    def run(self,content):
        terminos = {}
        tokens = []
        for single in self.regex.finditer(content):
            tokens.append(single.group(0))
            if single.group(0) not in terminos:
                terminos[single.group(0)] = {'CF':1}
            else:
                terminos[single.group(0)]['CF'] += 1
        content = self.regex.sub(" ",content)
        return {'content':content,'terminos':terminos, 'tokens':tokens}