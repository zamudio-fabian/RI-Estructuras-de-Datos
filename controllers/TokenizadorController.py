#!/usr/bin/env python
# -*- coding: utf-8 -*-
from repositories.CorpusRepository import *
from repositories.TokenRepository import *
from repositories.PostingRepository import *

class TokenizadorController():

    path = ''
    corpusRepository = None
    tokenRepository = None
    PostingRepository = None
    pathVacias = None

    def __init__(self,path,**options):
        self.path = path
        self.corpusRepository = CorpusRepository(path)
        self.tokenRepository = TokenRepository()
        self.PostingRepository = PostingRepository()
        self.pathVacias = options.get('pathVacias', None)

    def run(self):
        documentos = self.corpusRepository.getListDocuments()
        print "PROCESANDO DOCUMENTOS"
        response = self.tokenRepository.tokenizar(documentos,pathVacias = self.pathVacias)
        # Se guarda primero el archivo en ASCII para control y luego el archivo binario
        self.PostingRepository.save(response['terminos'])
        lexicon = self.PostingRepository.saveBinario(response['terminos'])
        result = {'lexicon':lexicon,'documentos':response['docs']}
        return result

        
