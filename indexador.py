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

    def __init__(self, path_corpus, path_vacias=None):
        self.path_corpus = path_corpus
        self.vacias = []
        self.lexicon = {}
        self.posting = {}
        self.documentos = []
        self.estructura_docs = {}
        self.estructura_corpus = 0
        self.peso_docs = {}
        self.peso_corpus = 0
        self.min_posting = None
        self.max_posting = None
        self.sum_posting = 0
        self.nombre_doc_actual = None
        self.doc_actual_tiene_terminos = None
        self.cargar_lista_vacias(path_vacias)

    def guardar_estadisticas(self):
        with codecs.open('index/estadisticas.txt', mode="w", encoding="utf-8") as file_est:
            file_est.write(u"ESTADÍSTICAS DE LA INDEXACIÓN\n")
            file_est.write("-------------------------------------------------\n")
            file_est.write(u"LONGITUDES DE POSTINGS\n")
            file_est.write(u"MÍNIMA: " + str(self.min_posting) + " documentos\n")
            file_est.write(u"MÁXIMA: " + str(self.max_posting) + " documentos\n")
            file_est.write(u"PROMEDIO: " + str(self.sum_posting / len(self.posting)) + " documentos\n")
            file_est.write("-------------------------------------------------\n")
            file_est.write(u"OVERHEAD DE LA COLECCIÓN\n")
            file_est.write(u"TAMAÑO COLECCIÓN: " + str(self.peso_corpus) + " bytes\n")
            file_est.write(u"TAMAÑO ESTRUCTURA: " + str(self.estructura_corpus) + " bytes\n")
            overhead = round(self.estructura_corpus / float(self.estructura_corpus + self.peso_corpus), 4) * 100
            file_est.write(u"OVERHEAD TOTAL: " + str(overhead) + "%\n")
            file_est.write("-------------------------------------------------\n")
            file_est.write(u"OVERHEAD DE CADA DOCUMENTO\n")
            for id_doc, doc in enumerate(self.estructura_docs):
                peso_doc = self.peso_docs[id_doc]
                peso_estructura_doc = self.estructura_docs[id_doc]
                overhead = round(peso_estructura_doc / float(peso_doc + self.peso_corpus), 4) * 100
                file_est.write("----\n")
                file_est.write(u"NOMBRE DOC: " + self.documentos[id_doc - 1 ] + "\n")
                file_est.write(u"TAMAÑO DOC: " + str(peso_doc) + " bytes\n")
                file_est.write(u"TAMAÑO ESTRUCTURA: " + str(peso_estructura_doc) + " bytes\n")
                file_est.write(u"OVERHEAD: " + str(overhead) + "%\n")

   
    def start(self):
        sys.stdout.write("Procesando documentos...")
        # Por cada documento en el directorio del corpus
        for raiz, dirs, nombres_docs in walk(unicode(self.path_corpus)):
            # Protección para no leer archivos de sistema MAC ej: .DS_store
            nombres_docs = [item for item in nombres_docs if item[0] != u'.']
            for doc_id, nombre_doc in enumerate(nombres_docs):
                self.estructura_docs[doc_id] = len(nombre_doc)
                path_doc = join(raiz, nombre_doc)
                self.analizar_documento(path_doc, doc_id)
                # Sumamos la estructura del doc altual al del corpus
                self.estructura_corpus += self.estructura_docs[doc_id]
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
        self.guardar_postings()
        # Guardamos los indices
        self.guardar_indice()
        # Guardar estadísticas
        self.guardar_estadisticas()

    def analizar_documento(self, path_doc, doc_id):
        # Leemos el archivo
        with codecs.open(path_doc, mode="r", encoding="utf-8", errors="ignore") as file_doc:
            texto_doc = file_doc.read()
            # Tokenizamos el texto
            tokens, terminos = Tokenizador.tokenizar(texto_doc, self.vacias)
            # Eliminamos palabras cortas o largas fuera del tokenizador para que no afecte a las queries
            # ya que me interesa que se quede con el caso OR 
            terminos = Tokenizador.minMaxLargo(terminos)
            self.peso_docs[doc_id] = sum(len(t) for t in terminos)
            self.peso_corpus += self.peso_docs[doc_id]
            # Guardamos los terminos
            self.update_vocabulario(tokens, terminos, doc_id)

    def update_vocabulario(self, tokens, terminos, doc_id):
        # Recorremos los tokens
        for termino in terminos:
            # Si el termino no esta en el vocabulario lo agrego
            if termino not in self.lexicon:
                # Tamaño necesario para almacenar el nombre del termino nuevo
                self.estructura_docs[doc_id] += len(termino)
                # Tamaño necesario para almacenar el nuevo record del lexicon TERM_ID | DF | PUNTERO
                self.estructura_docs[doc_id] += 4 * 3 
                self.lexicon[termino] = 0 # Document frecuency
                self.posting[termino] = [] # array de doc_id
            # Si el doc_id no esta en el listado de docs de ese termino lo agrego
            if doc_id not in self.posting[termino]:
                # Tamaño necesario para almacenar el nuevo posting
                self.estructura_docs[doc_id] += 4
                # Agrego el doc_id a la lista de posting
                self.posting[termino].append(doc_id) 
                self.lexicon[termino] += 1 # Aumento en 1 el documento frecuency

    @staticmethod
    def translate(to_translate):
        tabin = u"áéíóú"
        tabout = u"aeiou"
        tabin = [ord(char) for char in tabin]
        translate_table = dict(zip(tabin, tabout))
        return to_translate.translate(translate_table)

    @staticmethod
    def minMaxLargo(tokens):
        tokensAux = []
        for token in tokens:
            if len(token) >= 3 and len(token) <= 20 :
                tokensAux.append(token)
        return tokensAux

    # Tokenizador básico
    @staticmethod
    def tokenizar(texto, vacias = []):
        # To lower case
        texto = texto.lower()
        # Eliminamos caracteres especiales
        texto = Tokenizador.translate(texto)
        # Reemplazamos caracteres especiales con espacios
        texto = re.sub(u"[^a-zñ]|_", " ", texto)
        terminos = texto.split()
        tokens = terminos
        # Sacamos stopwords si es necesario
        if len(vacias) > 0:
            terminos = list(set(terminos) - set(vacias))
        return tokens, terminos

    def cargar_lista_vacias(self, path_vacias):
        if path_vacias is not None:
            with codecs.open(path_vacias, mode="r", encoding="utf-8") as file_vacias:
                texto_vacias = file_vacias.read()
                self.vacias = textp_vacias.split()

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

    def guardar_postings(self):
        packer = Struct(self.FORMATO_POSTING)
        puntero_posting = 0
        with open('index/postings.bin', mode="wb") as file_postings:
            for id_termino, termino in enumerate(self.terminos):
                largo_posting = len(self.posting[termino])
                if(self.min_posting == None or self.min_posting > largo_posting):
                        self.min_posting = largo_posting
                if(self.max_posting == None or self.max_posting < largo_posting):
                        self.max_posting = largo_posting
                self.sum_posting += largo_posting
                # Por cada documento guardo el doc_id
                for doc_id in sorted(self.posting[termino]):
                    file_postings.write(packer.pack(doc_id))

    def guardar_indice(self):
        packer = Struct(self.FORMATO_INDICE)
        puntero_posting = 0
        with open('index/lexicon.bin', mode="wb") as file_lexicon:
            for id_termino, termino in enumerate(self.terminos):
                # ID | DF | PUNTERO
                file_lexicon.write(packer.pack(id_termino, self.lexicon[termino] ,puntero_posting)) 
                puntero_posting += self.lexicon[termino] * 4 # DF * 4 = X Bytes


def start(dir_corpus, path_vacias=None):
    tokenizador = Tokenizador(dir_corpus, path_vacias=path_vacias)
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
    if "-v" in sys.argv:
        if sys.argv.index("-v") + 1 == len(sys.argv):
            print "ERROR: Debe ingresar el path del archivo con stopwords"
            sys.exit(1)
        else:
            path_vacias = sys.argv[sys.argv.index("-v") + 1]

    start(path_corpus,path_vacias = None)