#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import sys
from nltk.stem.snowball import SpanishStemmer
from models.LimpiarHtmlTagsRegla import *
from models.FechasRegla import *
from models.TelefonosRegla import *
from models.UrlRegla import *
from models.EmailRegla import *
from models.MinusculasRegla import *
from models.TranslateRegla import *
from models.LimpiadoBasicoRegla import *
from models.MinMaxCaracteresRegla import *
from models.AbreviaturasRegla import *
from models.NombresPropiosRegla import *
from models.NumerosRegla import *
from models.Documento import *

class TokenRepository:

    terminos = {}
    tokens = []
    reglasDocumento = []
    reglasTokens = []
    reglasEntities = []
    documentos = []
    fileNameTerminos = "results/terminos.txt"
    lista_vacias = []
    stemmer = None

    def __init__(self):

        self.reglasEntities.append(EmailRegla())
        self.reglasEntities.append(UrlRegla())
        self.reglasEntities.append(FechasRegla())
        self.reglasEntities.append(TelefonosRegla())
        self.reglasEntities.append(AbreviaturasRegla())
        self.reglasEntities.append(NombresPropiosRegla())
        self.reglasEntities.append(NumerosRegla())
        self.reglasDocumento.append(MinusculasRegla())
        self.reglasDocumento.append(TranslateRegla())
        self.reglasDocumento.append(LimpiarHtmlTagsRegla())
        self.reglasDocumento.append(LimpiadoBasicoRegla())
        self.reglasTokens.append(MinMaxCaracteresRegla())
        self.stemmer = SpanishStemmer()

    def tokenizar(self,documentos, **options):
        # INIT
        self.documentos = documentos
        self.tokens = []
        self.terminos = {}
        self.lista_vacias = []
        pathVacias = options.get('pathVacias', None)

        if pathVacias != None :
            print u"ANALIZANDO PALABRAS VACIAS"
            with codecs.open(pathVacias, mode='rt', encoding='utf-8') as vacias:
                content = vacias.read()
                for instancia in self.reglasDocumento:
                    content = instancia.run(content)

                palabras = content.strip().split()
                for palabra in palabras:
                    if palabra not in self.lista_vacias:
                        self.lista_vacias.append(palabra)

        # Procesamos cada documento
        indexDocumento = 0
        cantidadDocumentos = len(documentos)
        for documento in documentos:
            documento.terminos = {}
            documento.tokens = []
            content = documento.content
            tokensEntities = []
            # Aplicamos cada regla definida en self.reglasEntities para entidades
            for instancia in self.reglasEntities:
                response = instancia.run(content)
                content = response['content']
                # Agregamos los terminos a los del documento
                documento.terminos.update(response['terminos'])
                tokensEntities += response['tokens']


            # Aplicamos cada regla definida en self.reglasDocumento para normalizar
            for instancia in self.reglasDocumento:
                content = instancia.run(content)
            # Sacamos tokens de documentos
            tokensAux = self.getTokens(content)
            self.tokens = self.tokens + tokensAux + tokensEntities
            documento.tokens = tokensAux + tokensEntities

            # Aplicamos cada regla definida en self.reglasTokens
            for instancia in self.reglasTokens:
                tokensAux = instancia.run(tokensAux)

            # Sacamos palabras vacias
            if pathVacias != None :
                for token in tokensAux:
                    if token in self.lista_vacias:
                        tokensAux.remove(token)

            # Aplicamos Stemming excepto entidades
            tokensAux = self.stemmizar(tokensAux)

            terminosAux = self.getTerminos(tokensAux)
            documento.terminos.update(terminosAux)

            self.saveTerminosGlobal(documento)
            indexDocumento += 1
            porcentaje = (indexDocumento * 100) / cantidadDocumentos

            sys.stdout.write(u"\r"+str(int(porcentaje)).ljust(3)+u"% \u258F"+(u"\u2588"*int(porcentaje / 2)).ljust(50)+u"\u2595")
            sys.stdout.flush()

        print '\n'
        self.saveTerminosFile()
        # Armamos la respuesta
        response = {}
        response['terminos'] = self.terminos
        response['tokens'] = self.tokens
        response['documentos'] = documentos
        return response

    def getTokens(self,string):
        content = string.strip().split()
        # Return
        return content

    def getTerminos(self,tokens):
        terminos = {}
        for token in tokens:
            if token not in terminos:
                terminos[token] = {}
                terminos[token]['CF'] = 1
            else:
                terminos[token]['CF'] += 1
        return terminos

    def stemmizar(self,tokens):
        tokensAux = []
        for token in tokens:
            tokensAux.append(self.stemmer.stem(token))
        return tokensAux

    def saveTerminosGlobal(self,documento):
        terminos = {}
        for termino in documento.terminos:
            if termino not in self.terminos:
                self.terminos[termino] = {}
                self.terminos[termino]['CF'] = documento.terminos[termino]['CF']
                self.terminos[termino]['DOCS'] = [documento]
            else:
                self.terminos[termino]['CF'] += 1
                if documento not in self.terminos[termino]["DOCS"]:
                    self.terminos[termino]["DOCS"].append(documento)

    def saveTerminos(tokens,documento):
        if token not in self.terminos:
            self.terminos[token] = {}
            self.terminos[token]['CF'] = 1
            self.terminos[token]['DOCS'] = [documento]
        else:
            self.terminos[token]['CF'] += 1
            if documento not in self.terminos[token]["DOCS"]:
                self.terminos[token]["DOCS"].append(documento)

    def saveTerminosFile(self):
        with codecs.open(self.fileNameTerminos, mode="w", encoding="utf-8") as archivo:
            index = 0
            archivo.write('ID'.ljust(6))
            archivo.write('|')
            archivo.write('TERMINO'.ljust(30))
            archivo.write('|')
            archivo.write('CF'.ljust(6))
            archivo.write('|')
            archivo.write('DF'.ljust(6))
            archivo.write('\n')
            archivo.write('-'*50)
            archivo.write('\n')
            for termino in sorted(self.terminos.keys()):
                archivo.write(str(index).ljust(6))
                archivo.write('|')
                archivo.write(termino.ljust(30))
                archivo.write('|')
                archivo.write(str(self.terminos[termino]['CF']).ljust(6))
                archivo.write('|')
                archivo.write(str(len(self.terminos[termino]['DOCS'])).ljust(6))
                archivo.write('\n')
                index += 1