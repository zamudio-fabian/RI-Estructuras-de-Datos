#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from models.Regla import *

class UrlRegla(Regla):

    regex = None
    filename = 'results/urls.txt'

    def __init__(self):
        self.regex = re.compile(u"http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|((www\.[a-zA-Z0-9]+)|localhost)\.[a-zA-Z\.]+")
        
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