#!/usr/bin/env python
# -*- coding: utf-8 -*-
from repositories.CorpusRepository import *
from repositories.TokenRepository import *
from repositories.EstadisticasRepository import *

class TokenizadorController():

    path = ''
    corpusRepository = None
    tokenRepository = None
    EstadisticasRepository = None
    pathVacias = None

    def __init__(self,path,**options):
        self.path = path
        self.corpusRepository = CorpusRepository(path)
        self.tokenRepository = TokenRepository()
        self.EstadisticasRepository = EstadisticasRepository()
        self.pathVacias = options.get('pathVacias', None)

    def run(self):
        documentos = self.corpusRepository.getListDocuments()
        print "PROCESANDO DOCUMENTOS"
        response = self.tokenRepository.tokenizar(documentos,pathVacias = self.pathVacias)
        print "GENERANDO ESTADÍSTICAS"
        self.EstadisticasRepository.generar(response['tokens'],response['terminos'],response['documentos'])