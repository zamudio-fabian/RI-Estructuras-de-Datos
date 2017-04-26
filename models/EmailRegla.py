#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import codecs
from models.Regla import *

class EmailRegla(Regla):

    regex = None
    filename = 'results/emails.txt'

    def __init__(self):
        self.regex = re.compile(r"(?:[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*)@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])")

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