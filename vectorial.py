#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import codecs
import math
from struct import Struct
from os.path import join
from indexador import Tokenizador

class Buscador():
    FORMATO_POSTING_DOC_ID_TF = "I I"
    FORMATO_INDICE = "I I f I"

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
                doc_parts = documento.split(',')
                self.documentos.append({'name':doc_parts[0],'norma':float(doc_parts[1])})


    def cargar_lexicon(self):  
        # Formato del indice: [id_término, DF , IDF, Puntero]
        packer = Struct(self.FORMATO_INDICE)
        with open('index/lexicon.bin', mode="rb") as file_indice:
            bytes_indice = file_indice.read(packer.size)
            while bytes_indice:
                elementos_indice = packer.unpack(bytes_indice)
                self.lexicon[self.terminos[elementos_indice[0]]] = {'df':elementos_indice[1],'idf':elementos_indice[2],'puntero':elementos_indice[3]}
                bytes_indice = file_indice.read(packer.size)

    def cargar_postings(self, lista_terminos):  # Formato de las postings: df_término, secuencia de id_docs
        packer = Struct(self.FORMATO_POSTING_DOC_ID_TF)
        with open('index/postings.bin', mode="rb") as file_postings:
            doc_terminos = {}
            for termino in lista_terminos:
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
                        if doc_id not in doc_terminos:
                            doc_terminos[doc_id] = {}
                        if termino not in doc_terminos[doc_id]:
                            doc_terminos[doc_id][termino] = 0
                        doc_terminos[doc_id][termino] += 1 
            return doc_terminos

    def calcular_tfs(self, terminos):
        ret = {}
        for termino in terminos:
            ret[termino] = ret.get(termino, 0) + 1
        return ret


    def recuperar_archivos_opt_a(self, terminos_query, doc_terminos):
        ret = {}
        for index, documento in enumerate(doc_terminos):
            numerador = 0
            denominador = 0
            # Por cada termino en la query
            for termino in terminos_query:

                qtf = float(terminos_query.get(termino, 0)*0.5)
                qtf /= max(terminos_query.values())
                qtf += 0.5

                dtf = float(doc_terminos[documento].get(termino, 0))
                dtf /= max(doc_terminos[documento].values())

                idf = self.lexicon[termino]['idf']
                dtfidf = dtf*idf
                qtfidf = qtf*idf

                numerador += qtfidf * dtfidf
                denominador += qtfidf**2

            denominador = math.sqrt(denominador) * self.documentos[index]['norma']
            ret[documento] = numerador/denominador if denominador != 0 else 0
        return ret

    def recuperar_archivos_opt_b(self, terminos, query, terminos_archivos):
        ret = {}
        for archivo in terminos_archivos:
            numerador = 0
            denominador = 0
            for termino in query:
                if(not termino in terminos):
                    continue
                if(len(terminos_archivos[archivo]['terminos']) == 0):
                    continue

                qtf = float(query.get(termino, 0)*0.5)
                qtf /= max(query.values())
                qtf += 0.5

                dtf = float(terminos_archivos[archivo]['terminos'].get(termino, 0))
                dtf /= max(terminos_archivos[archivo]['terminos'].values())

                idf = 1
                dtfidf = dtf*idf
                qtfidf = math.log(1 + float(len(terminos_archivos))/terminos[termino]['df'],2) * idf

                numerador += qtfidf * dtfidf
                denominador += qtfidf**2

            denominador = math.sqrt(denominador) * terminos_archivos[archivo]['norma']
            ret[archivo] = numerador/denominador if denominador != 0 else 0
        return ret

    def recuperar_archivos_opt_c(self, terminos, query, terminos_archivos):
        ret = {}
        for archivo in terminos_archivos:
            numerador = 0
            denominador = 0
            for termino in query:
                if(not termino in terminos):
                    continue
                if(len(terminos_archivos[archivo]['terminos']) == 0):
                    continue

                qtf = float(query.get(termino, 0)*0.5)
                qtf /= max(query.values())
                qtf += 0.5

                dtf = float(terminos_archivos[archivo]['terminos'].get(termino, 0))
                dtf /= max(terminos_archivos[archivo]['terminos'].values())

                idf = self.calcular_idf(terminos_archivos, terminos, termino)
                dtfidf = dtf*idf
                qtfidf = math.log(1 + query.get(termino, 0),2) * idf

                numerador += qtfidf * dtfidf
                denominador += qtfidf**2

            denominador = math.sqrt(denominador) * terminos_archivos[archivo]['norma']
            ret[archivo] = numerador/denominador if denominador != 0 else 0
        return ret

    def cargar_busqueda(self, tokens_query, typeTFIDF):
        terminos_query = self.calcular_tfs(tokens_query)
        postings = self.cargar_postings(terminos_query)
        if (typeTFIDF == 'C') :
            ret = self.recuperar_archivos_opt_c(terminos_query, postings)
        elif (typeTFIDF == 'B') :
            ret = self.recuperar_archivos_opt_b(terminos_query, postings)
        else :
            ret = self.recuperar_archivos_opt_a(terminos_query, postings)
        ranking = sorted(ret.items(), key=lambda x: x[1], reverse=True)
        
        for r in xrange(0, min(15, len(ranking))):
            if(ranking[r][1] < 0.02):
                continue
            print (r+1),'-', self.documentos[ranking[r][0]]['name'], ranking[r][1]


if __name__ == "__main__":
    typeTFIDF = 'A'
    if "-h" in sys.argv:
        print "MODO DE USO: python vectorial.py [-t <A|B|C>]"
        sys.exit(0)
    if "-t" in sys.argv:
        if sys.argv.index("-t") + 1 == len(sys.argv):
            print "ERROR: Debe ingresar el tipo de ponderación que desea utilizar en la query"
            sys.exit(1)
        else:
            typeTFIDF = sys.argv[sys.argv.index("-t") + 1]

    buscador = Buscador()
    buscador.cargar_terminos()
    buscador.cargar_documentos()
    buscador.cargar_lexicon()
    texto_consulta = unicode(raw_input("Ingrese su consulta (/q para salir):"), "utf-8")
    while texto_consulta != "/q":
        tokens_query = Tokenizador.tokenizar(texto_consulta)
        buscador.cargar_busqueda(tokens_query, typeTFIDF)
        texto_consulta = unicode(raw_input("Ingrese su consulta (/q para salir):"), "utf-8")