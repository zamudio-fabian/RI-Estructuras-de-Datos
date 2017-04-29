#!/usr/bin/env python
# -*- coding: utf-8 -*-

from repositories.PostingRepository import *
from repositories.TokenRepository import *

class BooleanQueryRepository:

    postingRepository = None
    tokenRepository = None
    fileNameTerminos = "results/forhumans.txt"
    fileNamePosting = "results/postings.bin"
    lexicon = None
    documents = None

    def __init__(self):
        self.postingRepository = PostingRepository()
        self.tokenRepository = TokenRepository()
        self.lexicon = {}
        self.documents = []

    def setLexicon(self,lexicon):
        self.lexicon = lexicon

    def setDocuments(self,documents):
        self.documents = documents

    def getResults(self,query):
        partes = query.strip().split()
        parciales = []

        # Se obtienen los docs para cada termino
        for parte in partes:
            if (parte not in ['and','or','not']):
                terminoFromParte = self.tokenRepository.tokenizarString(parte).keys()[0]
                parciales.append(self.getPostingByTermino(terminoFromParte))
            else:
                parciales.append(parte)

        # Primero se áplica el NOT
        index = 0
        while index < len(parciales):
            item = parciales[index]
            if (item == 'not'):
                # Aplicamos la operación not al item siguiente
                parciales[index] = self.operacionNot(parciales[index+1])
                del parciales[index+1]
            index += 1

        index = 0
        # Luego se áplica AND y OR
        while index < len(parciales):
            item = parciales[index]
            if (item == 'and'):
                # Aplicamos la operación and al item siguiente y anterior
                parciales[index-1] = self.operacionAnd(parciales[index-1],parciales[index+1])
                # Se elimina el item correspondiente al AND
                del parciales[index]
                # Se elimina nuevamente ya que se desplazo todo un item por el del anterior
                del parciales[index]
            else:
                if (item == 'or'):
                    # Aplicamos la operación or al item siguiente y anterior
                    parciales[index-1] = self.operacionOr(parciales[index-1],parciales[index+1])
                    # Se elimina el item correspondiente al OR
                    del parciales[index]
                    # Se elimina nuevamente ya que se desplazo todo un item por el del anterior
                    del parciales[index]
                else: 
                    index += 1

        if (len(parciales) > 0):
            return sorted(parciales[0])
        else:
            return []

    def getPostingByTermino(self,termino):
        termino = self.lexicon.get(termino)
        if termino != None :
            # termino[1] => puntero archivo binario
            # termino[0] => DF - Document frecuency
            return self.postingRepository.getPosting(termino[1],termino[0])
        return []

    def operacionNot(self,arrayDocsId):
        s = set(arrayDocsId)
        temp = [x for x in self.documents if x not in s]
        return list(temp)

    def operacionAnd(self,array1,array2):
        set1 = set(array1)
        set2 = set(array2)
        return list(set1.intersection(set2))

    def operacionOr(self,array1,array2):
        set1 = set(array1)
        set2 = set(array2)
        return list(set1.union(set2))
        
            