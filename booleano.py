#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import codecs
from struct import Struct
from os.path import join
from indexador import Tokenizador
import time

class Buscador():
    FORMATO_POSTING = "I"
    FORMATO_INDICE = "I I I I I"
    FORMATO_SKIP = "I I"
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
                self.lexicon[self.terminos[elementos_indice[0]]] = {'df':elementos_indice[1],'puntero':elementos_indice[2],'size_skip':elementos_indice[3],'puntero_skip':elementos_indice[4]}
                bytes_indice = file_indice.read(packer.size)

    def cargar_postings_and_skips(self, lista_terminos):  # Formato de las postings: df_término, secuencia de id_docs
        packer = Struct(self.FORMATO_POSTING)
        packer_skip = Struct(self.FORMATO_SKIP)
        with open('index/postings.bin', mode="rb") as file_postings:
            with open('index/skip_list.bin', mode="rb") as file_skip:
                docs_por_termino = {}
                skips_por_terminos = {}
                for termino in lista_terminos:
                    docs_por_termino[termino] = []
                    skips_por_terminos[termino] = []
                    # Si el elemento esta en el lexico lo proceso de otra manera lo ignoro
                    if termino in self.lexicon:
                        pos_posting = self.lexicon[termino]['puntero']
                        pos_skip = self.lexicon[termino]['puntero_skip']
                        documento_frecuency = self.lexicon[termino]['df']
                        size_skip = self.lexicon[termino]['size_skip']
                        file_postings.seek(pos_posting)
                        file_skip.seek(pos_skip)
                        # Leo la posting
                        for i in xrange(documento_frecuency):
                            bytes_posting = file_postings.read(packer.size)
                            id_doc = packer.unpack(bytes_posting)[0]
                            docs_por_termino[termino].append(id_doc)
                        # Leo la skip list
                        for index in range(0,size_skip):
                            bytes_skip = file_skip.read(packer_skip.size)
                            elementos_skip = packer_skip.unpack(bytes_skip)
                            skips_por_terminos[termino].append({'doc_id':elementos_skip[0], 'doc_index':elementos_skip[1]})
            return docs_por_termino[lista_terminos[0]] , docs_por_termino[lista_terminos[1]], skips_por_terminos[lista_terminos[0]], skips_por_terminos[lista_terminos[1]]


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
                    # Leo la posting
                    for i in xrange(documento_frecuency):
                        bytes_posting = file_postings.read(packer.size)
                        id_doc = packer.unpack(bytes_posting)[0]
                        docs_por_termino[termino].append(id_doc)
            return docs_por_termino[lista_terminos[0]] , docs_por_termino[lista_terminos[1]]


    def obtener_ids_terminos(self, lista_terminos):
        lista_ids = []
        for termino in lista_terminos:
            if termino in self.terminos:
                lista_ids.append(self.terminos.index(termino))
        return lista_ids

    @staticmethod
    def intersectar(lista_1, lista_2):
        iteraciones = 0
        docs_id = []
        puntero1 = 0
        puntero2 = 0
        # Si todavia quedan doc_id en ambas listas
        while (puntero1 < len(lista_1) and puntero2 < len(lista_2)):
            iteraciones += 1
            doc_id_lista1 = lista_1[puntero1]
            doc_id_lista2 = lista_2[puntero2]
            # Si los doc_id son iguales
            if(doc_id_lista1 == doc_id_lista2):
                # Agrego a la lista el doc
                docs_id.append(doc_id_lista1)
                # Aumento ambos punteros
                puntero1 +=1
                puntero2 +=1
            # Si el doc_id de la lista 1 es menor a la de la lista 2
            elif (doc_id_lista1 < doc_id_lista2):
                puntero1 +=1
            # Si el doc_id de la lista 2 es menor o igual a la de la lista 1
            else:
                puntero2 +=1
        print 'ITERACIONES = '+ str(iteraciones)
        return docs_id

    @staticmethod
    def intersectar_con_skip(lista_1, lista_2, skip_list1, skip_list2):
        iteraciones = 0
        docs_id = []
        puntero1 = 0
        puntero2 = 0
        puntero_skip1 = 0
        puntero_skip2 = 0
        skip_list1 = sorted(skip_list1, key=lambda k: k['doc_id']) 
        skip_list2 = sorted(skip_list2, key=lambda k: k['doc_id'])
        # Si todavia quedan doc_id en ambas listas
        while (puntero1 < len(lista_1) and puntero2 < len(lista_2)):
            iteraciones += 1
            doc_id_lista1 = lista_1[puntero1]
            doc_id_lista2 = lista_2[puntero2]
            # Si los doc_id son iguales
            if(doc_id_lista1 == doc_id_lista2):
                # Agrego a la lista el doc
                docs_id.append(doc_id_lista1)
                # Aumento ambos punteros
                puntero1 +=1
                puntero2 +=1
            # Si el doc_id de la lista 1 es menor a la de la lista 2
            elif (doc_id_lista1 < doc_id_lista2):
                # Si quedan elementos en el skip_list1 y el valor de su DOC_ID es menor o igual al de la lista2 
                if (puntero_skip1 < len(skip_list1) and skip_list1[puntero_skip1]['doc_id'] <= doc_id_lista2):
                    # Busco el valor del skip inmediatamente inferior al de la lista2
                    while (puntero_skip1 < len(skip_list1) and skip_list1[puntero_skip1]['doc_id'] <= doc_id_lista2):
                        puntero1 = skip_list1[puntero_skip1]['doc_index']
                        puntero_skip1 +=1
                else:
                    puntero1 +=1
            # Si el doc_id de la lista 2 es menor o igual a la de la lista 1
            else:
                # Si quedan elementos en el skip_list2 y el valor de su DOC_ID es menor o igual al de la lista1 
                if (puntero_skip2 < len(skip_list2) and skip_list2[puntero_skip2]['doc_id'] <= doc_id_lista1):
                    # Busco el valor del skip inmediatamente inferior al de la lista1
                    while (puntero_skip2 < len(skip_list2) and skip_list2[puntero_skip2]['doc_id'] <= doc_id_lista1):
                        puntero2 = skip_list2[puntero_skip2]['doc_index']
                        puntero_skip2 +=1
                else:
                    puntero2 +=1
        print 'ITERACIONES = '+ str(iteraciones)
        return docs_id

    def cargar_busqueda(self, params, con_skip = False ):
        cant_params = len(params)
        operadores = [self.AND]
        if cant_params == 0:
            print u"ERROR: Debe ingresar al menos un término de busqueda"
        elif cant_params == 1 and params[0] in operadores:
            print u"ERROR: La busqueda no puede contener únicamente un operador sin términos"
        elif cant_params == 2 or (cant_params == 3 and params[1] not in operadores):
            print self.ERROR_CONSULTA
        elif cant_params > 3:
            print u"ERROR: Solo puede ingresar hasta 3 parámetros"
        else:
            start_time = time.time()
            if con_skip:
                respuesta = self.buscar_con_skip(params)
                print 'CON SKIP'
            else:
                respuesta = self.buscar(params)
                print 'NORMAL'
            print("--- %s seconds ---" % (time.time() - start_time))
            print 'CANTIDAD DE DOCUMENTOS = '+ str(len(respuesta))
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
        posting_1, posting_2 = self.cargar_postings(terminos_query)
        return self.intersectar(posting_1, posting_2)


    def buscar_con_skip(self, lista_parametros):
        terminos_query = []
        for parametro in lista_parametros:
            if parametro not in [self.AND]:
                terminos_query.append(parametro)
        posting_1, posting_2, skip_list_1, skip_list_2 = self.cargar_postings_and_skips(terminos_query)
        return self.intersectar_con_skip(posting_1, posting_2, skip_list_1, skip_list_2)


if __name__ == "__main__":

    con_skip = False

    if "-h" in sys.argv:
        print "MODO DE USO: python booleano.py [-s]"
        sys.exit(0)

    if "-s" in sys.argv:
        con_skip = True
        
    buscador = Buscador()
    buscador.cargar_terminos()
    buscador.cargar_documentos()
    buscador.cargar_lexicon()
    texto_consulta = unicode(raw_input("Ingrese su consulta (/q para salir):"), "utf-8")
    while texto_consulta != "/q":
        parametros_consulta = Tokenizador.tokenizar(texto_consulta)
        buscador.cargar_busqueda(parametros_consulta, con_skip)
        texto_consulta = unicode(raw_input("Ingrese su consulta (/q para salir):"), "utf-8")