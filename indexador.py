#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import codecs
from os import walk, makedirs
from os.path import join, isdir
from struct import Struct


class Tokenizador(object):
    FORMATO_POSTING = "I" # DOC_ID
    FORMATO_INDICE = "I I I" # ID_TERM DF PUNTERO_POSTING

    def __init__(self, path_corpus):
        self.path_corpus = path_corpus
        self.lexicon = {}
        self.posting = {}
        self.documentos = []
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
        # Guardamos los documentos
        self.guardar_documentos()
        # Guardamos los posting
        self.guardar_postings_lexicon()

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
        for posicion,token in enumerate(tokens):
            # Si el termino no esta en el vocabulario lo agrego
            if token not in self.lexicon:
                self.lexicon[token] = 0 # Document frecuency
                self.posting[token] = {} # array de doc_id:[pos]
            # Si el doc_id no esta en el listado de docs de ese token lo agrego
            if doc_id not in self.posting[token]:
                self.posting[token][doc_id] = [] # Agrego el doc_id a la lista de posting
                self.lexicon[token] += 1 # Aumento en 1 el documento frecuency

            #Agrego la posición a la posting
            self.posting[token][doc_id].append(posicion)

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
            for nombre_doc in self.documentos:
                file_documentos.write(nombre_doc + "\n")

    def guardar_postings_lexicon(self):
        packerPosting = Struct(self.FORMATO_POSTING)
        packerLexicon = Struct(self.FORMATO_INDICE)
        puntero_posting = 0
        with open('index/lexicon.bin', mode="wb") as file_lexicon:
            with open('index/postings.bin', mode="wb") as file_postings:
                for id_termino, termino in enumerate(self.terminos):
                    # Guardamos el lexicon
                    file_lexicon.write(packerLexicon.pack(id_termino, self.lexicon[termino] ,puntero_posting))
                    for doc_id in self.posting[termino]:
                        file_postings.write(packerPosting.pack(doc_id)) # Guardo DOC_ID
                        puntero_posting += packerPosting.size
                        file_postings.write(packerPosting.pack(len(self.posting[termino][doc_id]))) # Guardo TF
                        puntero_posting += packerPosting.size
                        for posicion in self.posting[termino][doc_id]:
                            puntero_posting += packerPosting.size
                            file_postings.write(packerPosting.pack(posicion)) # Guardo las posiciones


def start(dir_corpus):
    tokenizador = Tokenizador(dir_corpus)
    tokenizador.start()
    print u"Finalizado!"

if __name__ == "__main__":

    if "-h" in sys.argv:
        print "MODO DE USO: python booleano.py -c <path_directorio_corpus> [-v <path_archivo_stopwords>]"
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