# -*- coding: utf-8 -*-

import re
import sys
import time
import codecs
from os import walk, makedirs
from os.path import join, isdir
from struct import Struct
from compresion import codificar_numero_vl_str


class Tokenizador(object):
    MIN_LEN_TERM = 3
    MAX_LEN_TERM = 20

    def __init__(self, path_corpus, min_len=MIN_LEN_TERM, max_len=MAX_LEN_TERM):
        self.path_corpus = path_corpus
        self.min_len = min_len
        self.max_len = max_len
        self.vocabulario = {}
        self.id_doc = 0
        self.cantidad_docs = 0
        self.nombres_docs = []
        self.nombre_doc_actual = None
        self.doc_actual_tiene_terminos = None

    @staticmethod
    def translate(to_translate):
        tabin = u"áéíóú"
        tabout = u"aeiou"
        tabin = [ord(char) for char in tabin]
        translate_table = dict(zip(tabin, tabout))
        return to_translate.translate(translate_table)

    @staticmethod
    def tokenizar(texto):
        texto = texto.lower()
        texto = Tokenizador.translate(texto)
        texto = re.sub(u"[^a-zñ]|_", " ", texto)
        return texto.split()

    def analizar_corpus(self):
        for raiz, dirs, nombres_docs in walk(unicode(self.path_corpus)):
            for nombre_doc in nombres_docs:
                if (self.id_doc + 1) % 100 == 0:
                    sys.stdout.write("\r" + str(self.id_doc + 1) + " documentos procesados...")
                    sys.stdout.flush()
                self.nombre_doc_actual = nombre_doc
                self.doc_actual_tiene_terminos = False
                path_doc = join(raiz, nombre_doc)
                self.analizar_documento(path_doc)
                if self.doc_actual_tiene_terminos:
                    self.id_doc += 1
        self.cantidad_docs = self.id_doc
        sys.stdout.write("\n")
        sys.stdout.flush()

    def analizar_documento(self, path_doc):
        with codecs.open(path_doc, mode="r", encoding="utf-8", errors="ignore") as file_doc:
            texto_doc = file_doc.read()
            tokens = self.tokenizar(texto_doc)
            self.cargar_vocabulario(tokens)

    def cargar_vocabulario(self, tokens):
        for token in tokens:
            if self.min_len < len(token) < self.max_len:
                if token not in self.vocabulario:
                    self.vocabulario[token] = {}
                if self.id_doc in self.vocabulario[token]:
                    self.vocabulario[token][self.id_doc] += 1
                else:
                    self.vocabulario[token][self.id_doc] = 1
                if not self.doc_actual_tiene_terminos:
                    self.nombres_docs.append(self.nombre_doc_actual)
                    self.doc_actual_tiene_terminos = True


class Indexador(object):
    FORMATO_POSTING = "I"
    FORMATO_INDICE = "I I I"
    FILE_TERMINOS = "terminos.txt"
    FILE_DOCUMENTOS = "documentos.txt"
    FILE_POSTINGS = "postings.bin"
    FILE_POSTINGS_DGAPS = "postings_dgaps.bin"
    FILE_INDICE = "indice.bin"
    FILE_INDICE_DGAPS = "indice_dgaps.bin"
    FILE_TIEMPOS = "tiempos_compresion.txt"
    TIPO_VLENGTH = "VARIABLE-LENGTH"
    MODO_NORMAL = "NORMAL"
    MODO_DGAPS = "DGAPS"

    def __init__(self, vocabulario, lista_documentos):
        self.vocabulario = vocabulario
        self.path_terminos = join('index/', self.FILE_TERMINOS)
        self.path_documentos = join('index/', self.FILE_DOCUMENTOS)
        self.path_tiempos = join('index/', self.FILE_TIEMPOS)
        self.paths_postings = {self.TIPO_VLENGTH: {}}
        self.paths_indices = {self.TIPO_VLENGTH: {}}
        self.terminos = sorted([termino for termino in self.vocabulario])
        self.documentos = lista_documentos
        self.crear_directorios_compresiones('index/')
        self.tiempos = {
            self.TIPO_VLENGTH: {self.MODO_NORMAL: {}, self.MODO_DGAPS: {}}
        }
        self.indices = {
            self.TIPO_VLENGTH: {self.MODO_NORMAL: {}, self.MODO_DGAPS: {}}
        }

    def crear_directorios_compresiones(self, dir_indices):
        lista_dirs = [self.TIPO_VLENGTH]
        for dir_tf in lista_dirs:
            path_dir = join(dir_indices, dir_tf)
            self.crear_directorio(path_dir)
            self.paths_postings[dir_tf][self.MODO_NORMAL] = join(path_dir, self.FILE_POSTINGS)
            self.paths_postings[dir_tf][self.MODO_DGAPS] = join(path_dir, self.FILE_POSTINGS_DGAPS)
            self.paths_indices[dir_tf][self.MODO_NORMAL] = join(path_dir, self.FILE_INDICE)
            self.paths_indices[dir_tf][self.MODO_DGAPS] = join(path_dir, self.FILE_INDICE_DGAPS)

    @staticmethod
    def crear_directorio(path_dir):
        try:
            makedirs(path_dir)
        except OSError:
            if not isdir(path_dir):
                raise

    def guardar_terminos(self):
        with codecs.open(self.path_terminos, mode="w", encoding="utf-8") as file_terminos:
            for termino in self.terminos:
                file_terminos.write(termino + "\n")

    def guardar_nombres_documentos(self):
        with codecs.open(self.path_documentos, mode="w", encoding="utf-8") as file_documentos:
            for nombre_doc in self.documentos:
                file_documentos.write(nombre_doc + "\n")

    # noinspection PyTypeChecker
    def guardar_postings(self, tipo_compresion, modo_docs):
        packer = Struct(self.FORMATO_POSTING)
        self.inicializar_tiempos(tipo_compresion, modo_docs)
        pos_posting = 0
        bits_posting = ""
        with open(self.paths_postings[tipo_compresion][modo_docs], mode="wb") as file_postings:
            for id_termino, termino in enumerate(self.terminos):
                self.indices[tipo_compresion][modo_docs][id_termino] = {"inicio": pos_posting}
                df_termino = len(self.vocabulario[termino])
                tiempo_inicio = time.time()
                df_comprimido = str(codificar_numero_vl_str(df_termino))
                tiempo_compresion = time.time() - tiempo_inicio
                self.procesar_tiempo(tipo_compresion, modo_docs, tiempo_compresion)
                bits_posting += df_comprimido
                pos_posting += len(df_comprimido)
                bits_posting = self.guardar_bytes(bits_posting, file_postings, packer)
                id_doc_anterior = 0
                for id_doc in sorted(self.vocabulario[termino]):
                    tf_termino = self.vocabulario[termino][id_doc]
                    tiempo_inicio = time.time()
                    if modo_docs == self.MODO_DGAPS:
                        id_doc_actual = (id_doc + 1) - id_doc_anterior
                        id_doc_anterior = id_doc + 1
                    else:
                        id_doc_actual = id_doc + 1
                    id_doc_comprimido = str(codificar_numero_vl_str(id_doc_actual))
                    tf_comprimido = str(codificar_numero_vl_str(tf_termino))
                    tiempo_compresion = time.time() - tiempo_inicio
                    self.procesar_tiempo(tipo_compresion, modo_docs, tiempo_compresion)
                    bits_posting += id_doc_comprimido
                    bits_posting += tf_comprimido
                    pos_posting += len(id_doc_comprimido) + len(tf_comprimido)
                    bits_posting = self.guardar_bytes(bits_posting, file_postings, packer)
                    self.indices[tipo_compresion][modo_docs][id_termino]["fin"] = pos_posting
            if len(bits_posting) < 32:
                len_padding_final = 32 - len(bits_posting)
                bits_posting += "0" * len_padding_final
                self.guardar_bytes(bits_posting, file_postings, packer)

    @staticmethod
    def guardar_bytes(bits_posting, file_postings, packer):
        while len(bits_posting) >= 32:
            bloque_int = int(bits_posting[0:32], 2)
            file_postings.write(packer.pack(bloque_int))
            bits_posting = bits_posting[32:]
        return bits_posting

    # noinspection PyTypeChecker
    def guardar_indice(self, modo_compresion, modo_docs):
        packer = Struct(self.FORMATO_INDICE)
        with open(self.paths_indices[modo_compresion][modo_docs], mode="wb") as file_indice:
            for id_termino in sorted(self.indices[modo_compresion][modo_docs]):
                inicio = self.indices[modo_compresion][modo_docs][id_termino]["inicio"]
                fin = self.indices[modo_compresion][modo_docs][id_termino]["fin"]
                file_indice.write(packer.pack(id_termino, inicio, fin))

    def inicializar_tiempos(self, tipo_compresion, modo_docs):
        self.tiempos[tipo_compresion][modo_docs]["min"] = None
        self.tiempos[tipo_compresion][modo_docs]["max"] = None
        self.tiempos[tipo_compresion][modo_docs]["cant"] = 0
        self.tiempos[tipo_compresion][modo_docs]["suma"] = 0

    def procesar_tiempo(self, tipo_compresion, modo_docs, tiempo_descompresion):
        tiempo_minimo = self.tiempos[tipo_compresion][modo_docs]["min"]
        tiempo_maximo = self.tiempos[tipo_compresion][modo_docs]["max"]
        if not tiempo_minimo:
            self.tiempos[tipo_compresion][modo_docs]["min"] = tiempo_descompresion
        if not tiempo_maximo:
            self.tiempos[tipo_compresion][modo_docs]["max"] = tiempo_descompresion
        if tiempo_descompresion < tiempo_minimo:
            self.tiempos[tipo_compresion][modo_docs]["min"] = tiempo_descompresion
        if tiempo_descompresion > tiempo_maximo:
            self.tiempos[tipo_compresion][modo_docs]["max"] = tiempo_descompresion
        self.tiempos[tipo_compresion][modo_docs]["cant"] += 1
        self.tiempos[tipo_compresion][modo_docs]["suma"] += tiempo_descompresion

    # noinspection PyTypeChecker
    def guardar_tiempos(self):
        with codecs.open(self.path_tiempos, mode="w", encoding="utf-8") as file_tiempos:
            for tipo_compresion in self.tiempos:
                file_tiempos.write("---------------------------------------------------\n")
                file_tiempos.write(u"TIPO DE COMPRESIÓN: " + tipo_compresion + "\n")
                file_tiempos.write("\n")
                for modo_docs in self.tiempos[tipo_compresion]:
                    minimo = self.tiempos[tipo_compresion][modo_docs]["min"]
                    maximo = self.tiempos[tipo_compresion][modo_docs]["max"]
                    cantidad = self.tiempos[tipo_compresion][modo_docs]["cant"]
                    suma = self.tiempos[tipo_compresion][modo_docs]["suma"]
                    promedio = suma / float(cantidad)
                    file_tiempos.write(u"IDS DE DOCUMENTOS: " + modo_docs + "\n\n")
                    file_tiempos.write(u"TIEMPO MÍNIMO DE COMPRESIÓN: " + str(minimo) + " segundos\n")
                    file_tiempos.write(u"TIEMPO MÁXIMO DE COMPRESIÓN: " + str(maximo) + " segundos\n")
                    file_tiempos.write(u"TIEMPO PROMEDIO DE COMPRESIÓN: " + str(promedio) + " segundos\n")
                    file_tiempos.write(u"TIEMPO TOTAL DE COMPRESIÓN: " + str(suma) + " segundos\n")
                    file_tiempos.write("\n")


def main(dir_corpus):
    tokenizador = Tokenizador(dir_corpus)
    print u"Extrayendo los términos de la colección..."
    tokenizador.analizar_corpus()
    print u"Extracción terminada, generando los indices..."
    indexador = Indexador(tokenizador.vocabulario, tokenizador.nombres_docs)
    print u"Guardando los nombres de los términos..."
    indexador.guardar_terminos()
    print u"Guardando los nombres de los documentos..."
    indexador.guardar_nombres_documentos()
    print u"Usando el tipo de compresión: " + indexador.TIPO_VLENGTH + "..."
    for modo_docs in [indexador.MODO_NORMAL, indexador.MODO_DGAPS]:
        print u"Procesando los IDs de los documentos en modo: " + modo_docs + "..."
        print u"Comprimiendo y guardando las posting-lists..."
        indexador.guardar_postings(indexador.TIPO_VLENGTH, modo_docs)
        print u"Guardando el indice..."
        indexador.guardar_indice(indexador.TIPO_VLENGTH, modo_docs)
    print u"Guardando los tiempos de compresión..."
    indexador.guardar_tiempos()
    print u"Finalizado!"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "ERROR: Debe ingresar el directorio que contiene el corpus y el directorio destino de los indices."
        print "MODO DE USO: indexar_vectorial_ej11.py -c <path_corpus>"
    else:
    main(sys.argv[1])
