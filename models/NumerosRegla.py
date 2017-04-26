#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from models.Regla import *

class NumerosRegla(Regla):

    regex = None
    filename = 'results/numeros.txt'

    def __init__(self):
        self.regex = re.compile(u"(?:\d+\.)*\d+,\d+%? | [+-]?\d+(?:\.\d+)?")
        
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