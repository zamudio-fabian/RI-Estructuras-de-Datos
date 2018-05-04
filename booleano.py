#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import codecs
from struct import Struct
from os.path import join
from indexador import Tokenizador

class Buscador():
    FORMATO_POSTING_DOC_ID_TF = "I I"
    FORMATO_INDICE = "I I I"
    ADYACENTE = "ady"
    CERCA = "cerca"
    CERCA_DIFF = 5

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
        packer = Struct(self.FORMATO_POSTING_DOC_ID_TF)
        with open('index/postings.bin', mode="rb") as file_postings:
            docs_por_termino = {}
            for termino in lista_terminos:
                docs_por_termino[termino] = {}
                # Si el elemento esta en el lexico lo proceso de otra manera lo ignoro
                if termino in self.lexicon:
                    # Muevo el puntero
                    posicion_actual = self.lexicon[termino]['puntero']
                    file_postings.seek(posicion_actual)
                    documento_frecuency = self.lexicon[termino]['df']
                    for index in range(0,documento_frecuency):
                        # Leemos el DOC_ID y TF
                        bytes_posting_doc_id_tf = file_postings.read(packer.size)
                        doc_id_tf = packer.unpack(bytes_posting_doc_id_tf)
                        doc_id = doc_id_tf[0]
                        tf = doc_id_tf[1]
                        # Creamos un nuevo struct para leer las posiciones
                        packerPosiciones = Struct('I'*tf)
                        bytes_posting_posicion = file_postings.read(packerPosiciones.size)
                        docs_por_termino[termino][doc_id] = list(packerPosiciones.unpack(bytes_posting_posicion))
            return docs_por_termino

    @staticmethod
    def cerca(lista_1, lista_2, interseccion_docs, max_diff_posicion):
        docs_con_adyacentes = []
        for doc_id in interseccion_docs:
            # Mientras tenga elementos en ambos array
            while (lista_1[doc_id] and lista_2[doc_id]):
                # Si la diferencia de las posiciones es 1 encontre un ADYACENTE
                if(max_diff_posicion >= abs(lista_1[doc_id][0] - lista_2[doc_id][0])):
                    docs_con_adyacentes.append(doc_id)
                    break
                else:
                    # Si la posicion del termino A es menor a la del termino B
                    if(lista_1[doc_id][0] < lista_2[doc_id][0]):
                        # Saco la posición del termino A, ya que estoy seguro que la 
                        # proxima posición de B va a ser más grande la diferencia
                        lista_1[doc_id].pop(0)
                    else:
                        # Sino saco la posición del termino B
                        lista_2[doc_id].pop(0)
        return docs_con_adyacentes

    def cargar_busqueda(self, params):
        cant_params = len(params)
        operadores = [self.CERCA, self.ADYACENTE]
        if cant_params != 3:
            print u"ERROR: Debe ingresar tres términos en la busqueda"
        elif  (cant_params == 3 and params[0] not in operadores):
            print u"ERROR: La consulta debe tener el formato '[<ady> | <cerca>] <término1> <término2>'"
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
            if parametro not in [self.CERCA, self.ADYACENTE]:
                terminos_query.append(parametro)
        postings = self.cargar_postings(terminos_query)
        posting_1 = postings[terminos_query[0]]
        posting_2 = postings[terminos_query[1]]
        interseccion_docs = []
        for index in posting_1.keys():
            if index in posting_2:
                interseccion_docs.append(index)
        if lista_parametros[0] == self.CERCA:
            return self.cerca(posting_1, posting_2, interseccion_docs, self.CERCA_DIFF)
        elif lista_parametros[0] == self.ADYACENTE:
            return self.cerca(posting_1, posting_2, interseccion_docs, 1)


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