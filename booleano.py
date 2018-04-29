#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import codecs
from struct import Struct
from os.path import join
from indexador import Tokenizador

class Buscador():
    FORMATO_POSTING = "I"
    FORMATO_INDICE = "I I I"
    AND = "and"
    OR = "or"
    NOT = "not"
    ERROR_CONSULTA = u"ERROR: La consulta debe tener el formato '[<not>] <término> [(<and>|<or>|<and not>) <término>]'"

    def __init__(self):
        self.terminos = []
        self.documentos = []
        self.lexicon = {}

    def cargar_terminos(self):  # Archivo de texto con los nombres de los términos separados por saltos de línea
        with codecs.open('index/terminos.txt', mode="r", encoding="utf-8") as file_terminos:
            for termino in file_terminos:
                self.terminos.append(termino.strip())

    def cargar_documentos(self):  # Archivo de texto con los nombres de los documentos separados por saltos de línea
        with codecs.open('index/documentos.txt', mode="r", encoding="utf-8") as file_documentos:
            for documento in file_documentos:
                self.documentos.append(documento.strip())

    def cargar_lexicon(self):  # Formato del indice: [id_término, byte donde empieza la posting del término]
        packer = Struct(self.FORMATO_INDICE)
        with open('index/lexicon.bin', mode="rb") as file_indice:
            bytes_indice = file_indice.read(packer.size)
            while bytes_indice:
                elementos_indice = packer.unpack(bytes_indice)
                self.lexicon[self.terminos[elementos_indice[0]]] = {'df':elementos_indice[1],'puntero':elementos_indice[2]}
                bytes_indice = file_indice.read(packer.size)

    def cargar_postings(self, lista_terminos):  # Formato de las postings: df_término, secuencia de id_docs
        packer = Struct(self.FORMATO_POSTING)
        with open('index/postings.bin', mode="rb") as file_postings:
            docs_por_termino = {}
            for termino in lista_terminos:
                docs_por_termino[termino] = []
                # Si el elemento esta en el lexico lo proceso de otra manera lo ignoro
                if termino in self.lexicon:
                    pos_posting = self.lexicon[termino]['puntero']
                    documento_frecuency = self.lexicon[termino]['df']
                    file_postings.seek(pos_posting)
                    for i in xrange(documento_frecuency):
                        bytes_posting = file_postings.read(packer.size)
                        id_doc = packer.unpack(bytes_posting)[0]
                        docs_por_termino[termino].append(id_doc)
            return docs_por_termino

    def obtener_ids_terminos(self, lista_terminos):
        lista_ids = []
        for termino in lista_terminos:
            if termino in self.terminos:
                lista_ids.append(self.terminos.index(termino))
        return lista_ids

    @staticmethod
    def unir(lista_1, lista_2):
        return sorted(list(set(lista_1) | set(lista_2)))

    @staticmethod
    def intersectar(lista_1, lista_2):
        return sorted(list(set(lista_1) & set(lista_2)))

    @staticmethod
    def restar(lista_1, lista_2):
        return sorted(list(set(lista_1) - set(lista_2)))

    def cargar_busqueda(self, params):
        cant_params = len(params)
        operadores = [self.OR, self.AND, self.NOT]
        if cant_params == 0:
            print u"ERROR: Debe ingresar al menos un término de busqueda"
        elif cant_params == 1 and params[0] in operadores:
            print u"ERROR: La busqueda no puede contener únicamente un operador sin términos"
        elif cant_params == 2 or (cant_params == 3 and params[0] in operadores):
            print self.ERROR_CONSULTA
        elif cant_params > 3:
            print u"ERROR: Solo puede ingresar hasta 3 parámetros"
        else:
            respuesta = self.buscar(params)
            print u"Resultados de la búsqueda"
            if respuesta:
                print "ID_DOC\t\tNOMBRE_DOC"
                for id_doc in respuesta:
                    print str(id_doc) + "\t\t\t" + self.documentos[id_doc]
            else:
                print u"No se obtuvo ningún resultado"

    def buscar(self, lista_parametros):
        terminos_query = []
        for parametro in lista_parametros:
            if parametro not in [self.OR, self.AND, self.NOT]:
                terminos_query.append(parametro)
        postings = self.cargar_postings(terminos_query)
        posting_1 = postings[terminos_query[0]]
        posting_2 = postings[terminos_query[1]] if len(terminos_query) > 1 else []
        cant_params = len(lista_parametros)
        if cant_params == 1:
            return posting_1
        elif cant_params == 3:
            if lista_parametros[1] == self.OR:
                return self.unir(posting_1, posting_2)
            elif lista_parametros[1] == self.AND:
                return self.intersectar(posting_1, posting_2)
            elif lista_parametros[1] == self.NOT:
                return self.restar(posting_1, posting_2)


if __name__ == "__main__":
    buscador = Buscador()
    buscador.cargar_terminos()
    buscador.cargar_documentos()
    buscador.cargar_lexicon()
    texto_consulta = unicode(raw_input("Ingrese su consulta (/q para salir):"), "utf-8")
    while texto_consulta != "/q":
        parametros_consulta = Tokenizador.tokenizar(texto_consulta)
        buscador.cargar_busqueda(parametros_consulta)
        texto_consulta = unicode(raw_input("Ingrese su consulta (/q para salir):"), "utf-8")