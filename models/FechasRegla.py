#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from models.Regla import *

class FechasRegla(Regla):

    regex = None
    filename = 'results/fechas.txt'

    def __init__(self):
        self.regex = re.compile(u"(\d{1,2})[\/|-](\d{1,2})[\/|-](\d{1,4})|(\d{1,4})[\/|-](\d{1,2})[\/|-](\d{1,2})|[12]\d{3}-[12]\d{3}")
        
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