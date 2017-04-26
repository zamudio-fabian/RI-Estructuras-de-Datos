#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from models.Regla import *

class AbreviaturasRegla(Regla):

    regex = None
    filename = 'results/abreviaturas.txt'

    def __init__(self):
        self.regex = re.compile(u"([A-Z])+\.([A-Z])+\.([A-Z]+\.)*|(?:[A-Z][a-z]{1,2}\.)|([A-Z][a-z]+\.)+")
        
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