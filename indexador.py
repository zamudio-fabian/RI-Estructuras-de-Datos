#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import codecs
import resource
import os
from os.path import join, isdir
from os import walk, makedirs
from struct import Struct
import subprocess

class Tokenizador(object):
    FORMATO_POSTING = "I I" # DOC_ID | TF
    FORMATO_INDICE = "I I I" # ID_TERM DF PUNTERO_POSTING

    def __init__(self, path_corpus):
        self.path_corpus = path_corpus
        self.initStructures()
        self.lexicon = {} # Termino | DF
        self.terminos = []
        self.documentos = self.getDocs(path_corpus)
        self.nombre_doc_actual = None
        self.doc_actual_tiene_terminos = None
        self.crear_directorio()

    def getDocs(self, path_corpus):
        nombre_doc = []
        for raiz, dirs, nombres_docs in walk(unicode(self.path_corpus)):
            # Protección para no leer archivos de sistema MAC ej: .DS_store
            nombres_docs = [item for item in nombres_docs if item[0] != u'.']
        return nombres_docs

    def initStructures(self):
        self.triples = []


    def createChunks(self):
        index_doc = 0
        while index_doc < len(self.documentos):
            curDoc = self.documentos[index_doc]
            try:
                # Agregamos a la tripla general las del documento actual
                self.triples.append(self.generateTriplesFromTokens(self.processDoc(curDoc),index_doc))
                index_doc += 1
            except MemoryError as error:
                print "MEMORY ERROR!"
                # guardar chunk y limpiar estructuras!
                self.guardarChunkParcial()
                self.initStructures()
        # Guardamos el resto de chunks que no se guardaron
        self.guardarChunkParcial()
        self.sortChunk()
        self.saveChunksToBinarios()
        self.guardar_documentos()
        self.guardar_terminos()

    def sortChunk(self):
        subprocess.call("sort index/chunks.txt -o index/chunks.txt", shell=True)

    def saveChunksToBinarios(self):
        packer = Struct(self.FORMATO_POSTING)
        packerLexicon = Struct(self.FORMATO_INDICE)
        puntero = 0
        with open('index/lexicon.bin', mode="wb") as file_lexicon:
            with open('index/postings.bin', mode="wb") as file_postings:
                with open('index/chunks.txt', mode="r") as file_chunks:
                    for tripla in file_chunks:
                        actual_term = None
                        tripla = tripla.split(',')
                        if(actual_term != tripla[0]):
                            actual_term = tripla[0]
                            file_lexicon.write(packerLexicon.pack(self.terminos.index(actual_term), self.lexicon[actual_term], puntero))
                        # Guardamos el DOC_ID | TF
                        file_postings.write(packer.pack(int(tripla[1]), int(tripla[2])))
                        puntero += packer.size

    def processDoc(self, doc_name):
        with codecs.open(self.path_corpus+'/'+doc_name, mode="r", encoding="utf-8", errors='ignore') as file_doc:
            texto_doc = file_doc.read()
            # Tokenizamos el texto (lo más simple posible para llenar la memoria)
            return Tokenizador.tokenizar(texto_doc)

    def generateTriplesFromTokens(self, tokens, doc_id):
        triplesDoc = {}
        triplesDoc[doc_id] = {}
        for token in tokens:
            # Si no lo tengo en los terminos lo agrego
            if token not in self.terminos:
                self.terminos.append(token)
            # Aumento el DF del termino
            if token not in self.lexicon:
                self.lexicon[token] = 0
            self.lexicon[token] += 1
            # Genero el dic para ir sumando los tf
            if token not in triplesDoc[doc_id]:
                triplesDoc[doc_id][token] = 0
            triplesDoc[doc_id][token] += 1
        return triplesDoc
            

    def guardarChunkParcial(self):
        with codecs.open('index/chunks.txt', mode="w", encoding="utf-8") as file_chunks:
            for tripleDoc in self.triples:
                # Por cada triple list del doc
                for doc_id in tripleDoc:
                    for token in tripleDoc[doc_id]:
                        file_chunks.write(token +','+ str(doc_id) +','+ str(tripleDoc[doc_id][token]) + "\n")

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
        texto = re.sub(u"[^a-zñ]|_", " ", texto)
        tokens = texto.split()
        # Sacamos stopwords si es necesario
        return tokens

    def crear_directorio(self):
        try:
            makedirs('index')
        except OSError:
            if not isdir('index'):
                raise

    def guardar_documentos(self):
        with codecs.open('index/documentos.txt', mode="w", encoding="utf-8") as file_documentos:
            for nombre_doc in self.documentos:
                file_documentos.write(nombre_doc + "\n")

    def guardar_terminos(self):
        with codecs.open('index/terminos.txt', mode="w", encoding="utf-8") as file_terminos:
            for termino in self.terminos:
                file_terminos.write(termino + "\n")

def limit_memory(maxsize):
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (maxsize, hard))
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    print 'Memoria  Maxima Asignada  :', soft

def start(dir_corpus):
    limit_memory(1024 * 1024 * 1) # limite en cantidad de bytes: 1MB
    tokenizador = Tokenizador(dir_corpus)
    tokenizador.createChunks()
    print u"Finalizado!"

if __name__ == "__main__":
    if "-h" in sys.argv:
        print "MODO DE USO: python indexador.py -c <path_directorio_corpus> "
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