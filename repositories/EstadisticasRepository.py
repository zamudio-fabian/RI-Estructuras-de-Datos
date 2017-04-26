#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import operator
from models.Termino import *
from models.Documento import *

class EstadisticasRepository:

    tokens = []
    terminos = {}
    documentos = []
    fileNameTerminos = 'results/estadisticas.txt'
    fileNameFrecuentes = 'results/masmenosfrecuentes.txt'

    def __init__(self):
        pass

    def generar(self,tokens,terminos,documentos):
        self.tokens = tokens
        self.terminos = terminos
        self.documentos = sorted(documentos, key=self.orderDocumentos)

        cantidadDocumentos = None
        cantidadTokens = None
        cantidadTerminos = None
        promedioTokens = None
        promedioTerminos = None
        largoPromedioTermino = None
        cantidadTokensDocumentoCorto = None
        cantidadTokensDocumentoLargo = None
        cantidadTerminosDocumentoCorto = None
        cantidadTerminosDocumentoLargo = None
        terminosUnaAparicion = 0

        cantidadDocumentos = len(self.documentos)
        cantidadTokens = len(self.tokens)
        cantidadTerminos = len(self.terminos)
        promedioTokens = cantidadTokens / cantidadDocumentos
        promedioTerminos = cantidadTerminos / cantidadDocumentos

        acumuladoLargoTermino = 0
        for termino in self.terminos:
            acumuladoLargoTermino += len(termino)
            if (self.terminos[termino]['CF'] == 1):
                terminosUnaAparicion += 1

        documentoCorto = self.documentos[0]
        cantidadTerminosDocumentoCorto = len(documentoCorto.terminos)
        cantidadTokensDocumentoCorto = len(documentoCorto.tokens)

        documentoLargo = self.documentos[-1]
        cantidadTerminosDocumentoLargo = len(documentoLargo.terminos)
        cantidadTokensDocumentoLargo = len(documentoLargo.tokens)

        with codecs.open(self.fileNameTerminos, mode="w", encoding="utf-8") as archivo:
            archivo.write(u'GENERAL\n')
            archivo.write(u'='*50+'\n')
            archivo.write(u'Documentos ='+str(cantidadDocumentos)+'\n')
            archivo.write(u'Tokens totales ='+str(cantidadTokens)+'\n')
            archivo.write(u'Términos totales ='+str(cantidadTerminos)+'\n')
            archivo.write(u'Tokens promedio ='+str(promedioTokens)+'\n')
            archivo.write(u'Términos promedio ='+str(promedioTerminos)+'\n')
            archivo.write(u'Términos una sola aparición ='+str(terminosUnaAparicion)+'\n')
            archivo.write(u'\nDOCUMENTO CORTO '+documentoCorto.filename+'\n')
            archivo.write(u'='*50+'\n')
            archivo.write(u'Tokens ='+str(cantidadTokensDocumentoCorto)+'\n')
            archivo.write(u'Términos ='+str(cantidadTerminosDocumentoCorto)+'\n')
            archivo.write(u'\nDOCUMENTO LARGO '+documentoLargo.filename+'\n')
            archivo.write(u'='*50+'\n')
            archivo.write(u'Tokens ='+str(cantidadTokensDocumentoLargo)+'\n')
            archivo.write(u'Términos ='+str(cantidadTerminosDocumentoLargo)+'\n')

        responseMenos = self.terminos_menos_frecuentes(self.terminos)
        responseMas = self.terminos_mas_frecuentes(self.terminos)
        with codecs.open(self.fileNameFrecuentes, mode="w", encoding="utf-8") as archivo:
            archivo.write(u'MENOS FRECUENTES\n')
            archivo.write(u'='*50+'\n')
            for termino in responseMenos:
                archivo.write(termino[0].ljust(30))
                archivo.write('|')
                archivo.write(str(termino[1]).ljust(6))
                archivo.write('\n')
            archivo.write('\n')
            archivo.write(u'MÁS FRECUENTES\n')
            archivo.write(u'='*50+'\n')
            for termino in responseMas:
                archivo.write(termino[0].ljust(30))
                archivo.write('|')
                archivo.write(str(termino[1]).ljust(6))
                archivo.write('\n')

    def orderDocumentos(self,item):
        return item.tamanio

    def terminos_menos_frecuentes(self,terminos):
        listaAux = sorted(terminos.keys(), key=lambda x: (terminos[x]['CF']))[:10]
        response = {}
        for termino in listaAux:
            response[termino] = terminos[termino]["CF"]
        return sorted(response.items(), key=operator.itemgetter(1))

    def terminos_mas_frecuentes(self,terminos):
        listaAux = sorted(terminos.keys(), key=lambda x: (terminos[x]['CF']), reverse=True)[:10]
        response = {}
        for termino in listaAux:
            response[termino] = terminos[termino]["CF"]
        return sorted(response.items(), key=operator.itemgetter(1), reverse=True)
