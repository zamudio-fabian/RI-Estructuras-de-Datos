#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from models.Regla import *

class LimpiarHtmlTagsRegla(Regla):

    regexEntity = None
    regexTag = None

    def __init__(self):
        self.regexTag = re.compile(u"<(.|\n)*?>")
        self.regexEntity = re.compile(u"&[a-z]*;")
        
    def run(self,content):
        # Eliminamos tags básicos de ej: <img ... />
        content = self.regexTag.sub(" ", content)
        # Eliminamos entities de HTML ej: &quote;
        content = self.regexEntity.sub(" ", content)
        return content