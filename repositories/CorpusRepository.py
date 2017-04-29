#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
from os import listdir
from models.Documento import *
from os.path import relpath,join

class CorpusRepository:

    path = ''
    documentos = []

    def __init__(self,path):
        self.path = path

    def getListDocuments(self):
        self.documentos = []
        for documentName in listdir(relpath(self.path)):
            if (documentName[0] != u'.'): # Protección para no leer archivos de sistema MAC ej: .DS_store
                self.documentos.append(self.getDocument(documentName))
        return self.documentos

    def getFullStringFromDocument(self,documentName):
        filePath = join(self.path,documentName)
        with codecs.open(filePath, mode='rt', encoding='utf-8',errors='ignore') as fp:
            return fp.read()
        return None

    def getDocument(self,documentName):
        filePath = join(self.path,documentName)
        with codecs.open(filePath, mode='rt', encoding='utf-8',errors='ignore') as fp:
            return Documento(len(self.documentos)+1,documentName,fp.read())
        return None