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
    lista_vacias = []
    stemmer = None
    pathVacias = ''

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

    #########################################################
    # Metodo principal para inicializar variables y mandar a 
    # tokenizar dependendiendo el tipo de parametro
    # @param string  | array:Documents
    # @return dic
    #########################################################
    def tokenizar(self,objectToTokenizar, **options):
        # INIT
        self.tokens = []
        self.terminos = {}
        self.lista_vacias = []
        self.pathVacias = options.get('pathVacias', None)

        if self.pathVacias != None :
            print u"ANALIZANDO PALABRAS VACIAS"
            with codecs.open(pathVacias, mode='rt', encoding='utf-8') as vacias:
                content = vacias.read()
                for instancia in self.reglasDocumento:
                    content = instancia.run(content)

                palabras = content.strip().split()
                for palabra in palabras:
                    if palabra not in self.lista_vacias:
                        self.lista_vacias.append(palabra)

        # Caso particular si es una query y no un array de docs
        if (isinstance(objectToTokenizar,basestring)):
            return self.tokenizarString(objectToTokenizar)
        
        self.tokenizarDocumentos(objectToTokenizar)
        response = {}
        response['terminos'] = self.terminos
        response['docs'] = self.documentos
        return response


    #########################################################
    # Aplica reglas de tokenizador a un string para obtener sus terminos
    # @param string
    # @return dic
    #########################################################
    def tokenizarString(self,content):
        documentoTerminos = {}
        # Aplicamos cada regla definida en self.reglasEntities para entidades
        for instancia in self.reglasEntities:
            response = instancia.run(content)
            content = response['content']
            documentoTerminos.update(response['terminos'])

        # Aplicamos cada regla definida en self.reglasDocumento para normalizar
        for instancia in self.reglasDocumento:
            content = instancia.run(content)

        # Sacamos tokens de documentos
        tokensDocumento = self.getTokens(content)

        # Aplicamos cada regla definida en self.reglasTokens
        for instancia in self.reglasTokens:
            tokensDocumento = instancia.run(tokensDocumento)

        # Sacamos palabras vacias
        if self.pathVacias != None :
            for token in tokensDocumento:
                if token in self.lista_vacias:
                    tokensDocumento.remove(token)

        # Aplicamos Stemming excepto entidades
        tokensDocumento = self.stemmizar(tokensDocumento)
        
        terminosAux = self.getTerminos(tokensDocumento)
        documentoTerminos.update(terminosAux)

        return documentoTerminos

    #########################################################
    # Recorre un array de documentos y aplicar las reglas de
    # tokenización y obtener los terminos de cada uno
    # @param array:Documentos
    # @return dic
    #########################################################
    def tokenizarDocumentos(self,documentos):
        # Procesamos cada documento
        indexDocumento = 0
        cantidadDocumentos = len(documentos)
        for documento in documentos:
            self.documentos.append(documento.id)
            documento.terminos = {}
            content = documento.content

            documento.terminos = self.tokenizarString(content)

            self.saveTerminosGlobal(documento)
            indexDocumento += 1
            porcentaje = (indexDocumento * 100) / cantidadDocumentos

            sys.stdout.write(u"\r"+str(int(porcentaje)).ljust(3)+u"% \u258F"+(u"\u2588"*int(porcentaje / 2)).ljust(50)+u"\u2595")
            sys.stdout.flush()

        print '\n'

    #########################################################
    # Hace un strip para obtener los tokens
    # @param string
    # @return array
    #########################################################
    def getTokens(self,string):
        content = string.strip().split()
        # Return
        return content

    #########################################################
    # Elimina las repeticiones de tokens
    # @param array
    # @return dic
    #########################################################
    def getTerminos(self,tokens):
        terminos = {}
        for token in tokens:
            if token not in terminos:
                terminos[token] = {}
                terminos[token]['CF'] = 1
            else:
                terminos[token]['CF'] += 1
        return terminos

    #########################################################
    # Aplica Stemmer español a un array de tokens
    # @param array
    # @return string
    #########################################################
    def stemmizar(self,tokens):
        tokensAux = []
        for token in tokens:
            tokensAux.append(self.stemmer.stem(token))
        return tokensAux

    #########################################################
    # Si existe un termino en un doc que no este en los terminos
    # globales lo agrega
    # @param Documento
    #########################################################
    def saveTerminosGlobal(self,documento):
        terminos = {}
        for termino in documento.terminos:
            if termino not in self.terminos:
                self.terminos[termino] = {}
                self.terminos[termino]['CF'] = documento.terminos[termino]['CF']
                self.terminos[termino]['DOCS'] = [documento.id]
            else:
                self.terminos[termino]['CF'] += 1
                if documento not in self.terminos[termino]["DOCS"]:
                    self.terminos[termino]["DOCS"].append(documento.id)
    