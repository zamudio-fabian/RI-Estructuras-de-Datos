#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from models.Regla import *

class LimpiadoBasicoRegla(Regla):

    regex = None

    def __init__(self):
        self.regex = re.compile(u"[^a-z0-9\s]")
        
    def run(self,content):
        content = self.regex.sub(" ", content)
        return content

    