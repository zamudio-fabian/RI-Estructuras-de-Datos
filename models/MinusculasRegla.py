#!/usr/bin/env python
# -*- coding: utf-8 -*-
from models.Regla import *

class MinusculasRegla(Regla):

    def __init__(self):
        pass
        
    def run(self,content):
        content = content.lower();
        return content
        