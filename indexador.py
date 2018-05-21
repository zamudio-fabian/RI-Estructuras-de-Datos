#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import codecs
from os import walk, makedirs
from os.path import join, isdir
from struct import Struct
import math


class Tokenizador(object):
    FORMATO_POSTING = "I" # DOC_ID
    FORMATO_INDICE = "I I f I" # ID_TERM DF IDF PUNTERO_POSTING

    def __init__(self, path_corpus):
        self.path_corpus = path_corpus
        self.lexicon = {}
        self.posting = {}
        self.documentos = []
        self.normas_docs = {}
        self.idf_terminos = {}
        self.nombre_doc_actual = None
        self.doc_actual_tiene_terminos = None

    def start(self):
        sys.stdout.write("Procesando documentos...")
        # Por cada documento en el directorio del corpus
        for raiz, dirs, nombres_docs in walk(unicode(self.path_corpus)):
            # Protección para no leer archivos de sistema MAC ej: .DS_store
            nombres_docs = [item for item in nombres_docs if item[0] != u'.']
            for doc_id, nombre_doc in enumerate(nombres_docs):
                path_doc = join(raiz, nombre_doc)
                self.analizar_documento(path_doc, doc_id)
                self.documentos.append(nombre_doc)
        # Creamos el directorio del indice
        self.crear_directorio()
        # Ordenamos los terminos 
        self.terminos = sorted([termino for termino in self.lexicon])
        # Guardamos los terminos
        self.guardar_terminos()
        # Guardamos los posting
        self.guardar_postings_lexicon()
        # Guardamos los documentos
        self.guardar_documentos()

    def analizar_documento(self, path_doc, doc_id):
        # Leemos el archivo
        with codecs.open(path_doc, mode="r", encoding="utf-8", errors="ignore") as file_doc:
            texto_doc = file_doc.read()
            # Tokenizamos el texto
            tokens = Tokenizador.tokenizar(texto_doc)
            # Eliminamos palabras cortas o largas fuera del tokenizador para que no afecte a las queries
            # Guardamos los terminos
            self.update_vocabulario(tokens, doc_id)

    def update_vocabulario(self, tokens, doc_id):
        # Recorremos los tokens
        for token in tokens:
            # Si el termino no esta en el vocabulario lo agrego
            if token not in self.lexicon:
                self.lexicon[token] = 0 # Document frecuency
                self.posting[token] = {} # array de doc_id
            # Si el doc_id no esta en el listado de docs de ese token lo agrego
            if doc_id not in self.posting[token]:
                self.posting[token][doc_id] = 0 # Seteo el TF en 0
                self.lexicon[token] += 1 # Aumento en 1 el DF
            # Aumento en 1 el TF de ese token en ese documento
            self.posting[token][doc_id] += 1

    @staticmethod
    def translate(to_translate):
        tabin = u"áéíóú"
        tabout = u"aeiou"
        tabin = [ord(char) for char in tabin]
        translate_table = dict(zip(tabin, tabout))
        return to_translate.translate(translate_table)

    # Tokenizador básico
    @staticmethod
    def tokenizar(texto):
        # To lower case
        texto = texto.lower()
        # Eliminamos caracteres especiales
        texto = Tokenizador.translate(texto)
        # Reemplazamos caracteres especiales con espacios
        texto = re.sub(u"[^a-zñ0-9]|_", " ", texto)
        tokens = texto.split()
        # Sacamos stopwords si es necesario
        return tokens

    def crear_directorio(self):
        try:
            makedirs('index')
        except OSError:
            if not isdir('index'):
                raise

    def guardar_terminos(self):
        with codecs.open('index/terminos.txt', mode="w", encoding="utf-8") as file_terminos:
            for termino in self.terminos:
                file_terminos.write(termino + "\n")

    def guardar_documentos(self):
        with codecs.open('index/documentos.txt', mode="w", encoding="utf-8") as file_documentos:
            for doc_id, nombre_doc in enumerate(self.documentos):
                file_documentos.write(nombre_doc +','+str(self.normas_docs[doc_id])+"\n")

    def calcular_idf(self, termino):
        return math.log(float(len(self.documentos))/self.lexicon[termino], 2)

    def guardar_postings_lexicon(self):
        packerPosting = Struct(self.FORMATO_POSTING)
        packerLexicon = Struct(self.FORMATO_INDICE)
        puntero_posting = 0
        with open('index/lexicon.bin', mode="wb") as file_lexicon:
            with open('index/postings.bin', mode="wb") as file_postings:
                for id_termino, termino in enumerate(self.terminos):
                    # Guardamos el lexicon
                    self.idf_terminos[termino] = self.calcular_idf(termino)
                    file_lexicon.write(packerLexicon.pack(id_termino, self.lexicon[termino] , self.idf_terminos[termino] ,puntero_posting))
                    for doc_id in self.posting[termino]:
                        # Guardo DOC_ID
                        file_postings.write(packerPosting.pack(doc_id)) 
                        puntero_posting += packerPosting.size
                        # Guardo TF
                        file_postings.write(packerPosting.pack(self.posting[termino][doc_id])) 
                        puntero_posting += packerPosting.size
                        # Voy calculando las normas de los docs
                        if(doc_id not in self.normas_docs):
                            self.normas_docs[doc_id] = 0
                        self.normas_docs[doc_id] += (self.idf_terminos[termino]*self.posting[termino][doc_id])**2
        # Hago la raiz de las normas
        for doc_id in self.normas_docs:
            self.normas_docs[doc_id] = math.sqrt(self.normas_docs[doc_id])

    def guardar_normas(self):
        print 'IDF'
        print self.idf_terminos


def start(dir_corpus):
    tokenizador = Tokenizador(dir_corpus)
    tokenizador.start()
    print u"Finalizado!"

if __name__ == "__main__":

    if "-h" in sys.argv:
        print "MODO DE USO: python indexador.py -c <path_directorio_corpus> [-v <path_archivo_stopwords>]"
        sys.exit(0)
    if len(sys.argv) < 3:
        print "ERROR: "
        sys.exit(1)
    if "-c" in sys.argv:
        if sys.argv.index("-c") + 1 == len(sys.argv):
            print "ERROR: Debe ingresar el directorio del corpus"
            sys.exit(1)
        else:
            path_corpus = sys.argv[sys.argv.index("-c") + 1]

    start(path_corpus)