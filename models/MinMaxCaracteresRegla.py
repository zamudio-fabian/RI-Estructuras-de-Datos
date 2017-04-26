#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from models.Regla import *

class MinMaxCaracteresRegla(Regla):

    minCarac = 3
    maxCarac = 20

    def __init__(self):
        pass
        
    def run(self,tokens):
        tokensAux = []
        for token in tokens:
            if len(token) >= self.minCarac and len(token) <= self.maxCarac :
                tokensAux.append(token)
        return tokensAux

    