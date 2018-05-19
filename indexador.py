#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import codecs
import math
from os import walk, makedirs
from os.path import join, isdir
from struct import Struct


class Tokenizador(object):
    FORMATO_POSTING = "I" # DOC_ID
    FORMATO_INDICE = "I I I I I" # ID_TERM DF PUNTERO_POSTING CANT_ELEM_SKIP PUNTERO_SKIP_LIST
    FORMATO_SKIP_LIST = "I I" # DOC_ID | posición array

    def __init__(self, path_file):
        self.path_file = path_file
        self.lexicon = {}
        self.posting = {}
        self.termino_skip_list = {}
        self.documentos = []
        self.terminos = [];

    def start(self):
        sys.stdout.write("Procesando documentos...")
        self.analizar_documento(path_file)
        # Creamos el directorio del indice
        self.crear_directorio()
        # Guardamos los terminos
        self.guardar_terminos()
        # Guardamos los posting
        self.guardar_postings_skip_list()
        # Guardamos los indices
        self.guardar_indice()

    def analizar_documento(self, path_file):
        # Leemos el archivo
        puntero_posting = 0
        with open(path_file, mode="r") as file_doc:
            for index, linea in enumerate(file_doc):
                elementos_linea = linea.split(':')
                self.terminos.append(Tokenizador.translate(elementos_linea[0]));
                self.lexicon[index] = int(elementos_linea[1])
                self.posting[index] = map(int,elementos_linea[2].replace(',\n','').split(','))

    def update_vocabulario(self, tokens, doc_id):
        # Recorremos los tokens
        for token in tokens:
            # Si el termino no esta en el vocabulario lo agrego
            if token not in self.lexicon:
                self.lexicon[token] = 0 # Document frecuency
                self.posting[token] = [] # array de doc_id
            # Si el doc_id no esta en el listado de docs de ese token lo agrego
            if doc_id not in self.posting[token]:
                self.posting[token].append(doc_id) # Agrego el doc_id a la lista de posting
                self.lexicon[token] += 1 # Aumento en 1 el documento frecuency

    @staticmethod
    def translate(to_translate):
        to_translate = to_translate.decode('utf-8', errors='ignore')
        tabin = [u'áéíóúñ', u'àèìòùñ', u'äëïöüñ', u'âêîôûñ']
        tabout = u'aeioun'
        translate_table = {}
        for i in xrange(0, len(tabin)):
            translate_table.update(dict(zip([ord(char) for char in tabin[i]], tabout)))
        
        return to_translate.translate(translate_table).encode('utf-8')


    # Tokenizador básico
    @staticmethod
    def tokenizar(texto, vacias = []):
        # To lower case
        texto = texto.lower()
        # Eliminamos caracteres especiales
        texto = Tokenizador.translate(texto)

        # Reemplazamos caracteres especiales con espacios
        texto = re.sub(u"[^a-zñ]|_", " ", texto)
        print 'texto = '+ texto
        tokens = texto.split()
        # Sacamos stopwords si es necesario
        if len(vacias) > 0:
            tokens = list(set(tokens) - set(vacias))
        return tokens

    def cargar_lista_vacias(self, path_vacias):
        if path_vacias is not None:
            with codecs.open(path_vacias, mode="r", encoding="utf-8", errors='ignore') as file_vacias:
                texto_vacias = file_vacias.read()
                self.vacias = textp_vacias.split()

    def crear_directorio(self):
        try:
            makedirs('index')
        except OSError:
            if not isdir('index'):
                raise

    def guardar_terminos(self):
        with codecs.open('index/terminos.txt', mode="w", encoding="utf-8", errors='ignore') as file_terminos:
            for termino in self.terminos:  
                file_terminos.write(termino + "\n")
                

    def guardar_documentos(self):
        with codecs.open('index/documentos.txt', mode="w", encoding="utf-8") as file_documentos:
            for nombre_doc in self.documentos:
                file_documentos.write(nombre_doc + "\n")

    def guardar_postings_skip_list(self):
        packer = Struct(self.FORMATO_POSTING)
        puntero_posting = 0
        with open('index/postings.bin', mode="wb") as file_postings:
            for index, termino in enumerate(self.terminos):
                termino_id = index
                delta_gap = 0
                id_anterior = 0
                postingOrdenadas = sorted(self.posting[termino_id])
                # Por cada documento guardo el doc_id
                largo_posting = len(self.posting[termino_id])
                salto_skip = math.ceil(math.sqrt(largo_posting))
                indexSkip = salto_skip 
                # Creamos la skip para ese termino
                self.termino_skip_list[termino_id] = {}
                # Por cada documento guardo el doc_id
                for nro_doc,doc_id in enumerate(postingOrdenadas):
                    delta_gap = doc_id - id_anterior
                    id_anterior = doc_id
                    file_postings.write(packer.pack(delta_gap))
                    # Si es el elemento que tiene que ir a la skip list lo guardo
                    if nro_doc == indexSkip:
                        self.termino_skip_list[termino_id][doc_id] = nro_doc - 1
                        indexSkip += salto_skip

    def guardar_indice(self):
        packer = Struct(self.FORMATO_INDICE)
        packer_skip_list = Struct(self.FORMATO_SKIP_LIST)
        puntero_posting = 0
        puntero_skip = 0
        with open('index/skip_list.bin', mode="wb") as file_skip:
            with open('index/lexicon.bin', mode="wb") as file_lexicon:
                for index, termino in enumerate(self.terminos):
                    termino_id = index
                    # ID_TERM | DF | PUNTERO_POSTING | CANT_ELEM_SKIP | PUNTERO_SKIP_LIST
                    para_grabar = packer.pack(termino_id, self.lexicon[termino_id] ,puntero_posting, len(self.termino_skip_list[termino_id]) , puntero_skip)
                    file_lexicon.write(para_grabar) 
                    puntero_posting += self.lexicon[termino_id] * 4 # DF * 4 = X Bytes
                    puntero_skip += len(self.termino_skip_list[termino_id]) * 8 # N * (4+4) 
                    for doc_id in self.termino_skip_list[termino_id]:
                        file_skip.write(packer_skip_list.pack(doc_id, self.termino_skip_list[termino_id][doc_id])) 


def start(dir_corpus):
    tokenizador = Tokenizador(dir_corpus)
    tokenizador.start()
    print u"Finalizado!"

if __name__ == "__main__":

    if "-h" in sys.argv:
        print "MODO DE USO: python indexador.py -f <path_directorio_file>"
        sys.exit(0)
    if len(sys.argv) < 3:
        print "MODO DE USO: python indexador.py -f <path_directorio_file>"
        sys.exit(1)
    if "-f" in sys.argv:
        if sys.argv.index("-f") + 1 == len(sys.argv):
            print "ERROR: Debe ingresar el archivo que contiene la lista de terminos con sus document frecuency y posting list"
            sys.exit(1)
        else:
            path_file = sys.argv[sys.argv.index("-f") + 1]

    start(path_file)