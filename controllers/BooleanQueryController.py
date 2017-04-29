#!/usr/bin/env python
# -*- coding: utf-8 -*-
from repositories.BooleanQueryRepository import *

class BooleanQueryController():

    booleanQueryRepository = None

    def __init__(self):
        self.booleanQueryRepository = BooleanQueryRepository()

    def setParams(self,params):
        self.booleanQueryRepository.setLexicon(params['lexicon'])
        self.booleanQueryRepository.setDocuments(params['documentos'])

    def getResults(self,query):
        return self.booleanQueryRepository.getResults(query)
        

        
