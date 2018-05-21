# -*- coding: utf-8 -*-

import sys
import time
import codecs
from struct import Struct
from os.path import join
from compresion import decodificar_numeros_vl_str, convertir_a_bin


class DescompresorPostings(object):
    FORMATO_POSTING = "I"
    FORMATO_INDICE = "I I I"
    FILE_POSTINGS = "postings.bin"
    FILE_POSTINGS_DGAPS = "postings_dgaps.bin"
    FILE_INDICE = "indice.bin"
    FILE_INDICE_DGAPS = "indice_dgaps.bin"
    FILE_TIEMPOS = "tiempos_descompresion.txt"
    TIPO_VLENGTH = "VARIABLE-LENGTH"
    MODO_NORMAL = "NORMAL"
    MODO_DGAPS = "DGAPS"

    def __init__(self, dir_indices):
        self.paths_postings = {self.TIPO_VLENGTH: {}}
        self.paths_indices = {self.TIPO_VLENGTH: {}}
        self.path_tiempos = join(dir_indices, self.FILE_TIEMPOS)
        self.cargar_directorios_compresiones(dir_indices)
        self.tiempos = {
            self.TIPO_VLENGTH: {self.MODO_NORMAL: {}, self.MODO_DGAPS: {}}
        }
        self.indices = {
            self.TIPO_VLENGTH: {self.MODO_NORMAL: {}, self.MODO_DGAPS: {}}
        }

    def cargar_directorios_compresiones(self, dir_indices):
        lista_dirs = [self.TIPO_VLENGTH]
        for dir_tf in lista_dirs:
            path_dir = join(dir_indices, dir_tf)
            self.paths_postings[dir_tf][self.MODO_NORMAL] = join(path_dir, self.FILE_POSTINGS)
            self.paths_postings[dir_tf][self.MODO_DGAPS] = join(path_dir, self.FILE_POSTINGS_DGAPS)
            self.paths_indices[dir_tf][self.MODO_NORMAL] = join(path_dir, self.FILE_INDICE)
            self.paths_indices[dir_tf][self.MODO_DGAPS] = join(path_dir, self.FILE_INDICE_DGAPS)

    # noinspection PyTypeChecker
    def cargar_indice(self, tipo_compresion, modo_docs):
        packer = Struct(self.FORMATO_INDICE)
        with open(self.paths_indices[tipo_compresion][modo_docs], mode="rb") as file_indice:
            bytes_indice = file_indice.read(packer.size)
            while bytes_indice:
                elementos_indice = packer.unpack(bytes_indice)
                indice = self.indices[tipo_compresion][modo_docs]
                id_termino = elementos_indice[0]
                indice[id_termino] = {}
                indice[id_termino]["inicio"] = elementos_indice[1]
                indice[id_termino]["fin"] = elementos_indice[2]
                bytes_indice = file_indice.read(packer.size)

    # noinspection PyTypeChecker
    def cargar_postings(self, tipo_compresion, modo_docs):
        packer = Struct(self.FORMATO_POSTING)
        self.inicializar_tiempos(tipo_compresion, modo_docs)
        with open(self.paths_postings[tipo_compresion][modo_docs], mode="rb") as file_postings:
            bits_posting = ""
            pos_posting = 0
            offset_posicion = 0
            for id_termino in sorted(self.indices[tipo_compresion][modo_docs]):
                inicio_posting = self.indices[tipo_compresion][modo_docs][id_termino]["inicio"]
                fin_posting = self.indices[tipo_compresion][modo_docs][id_termino]["fin"]
                while pos_posting < fin_posting:
                    bytes_leidos = file_postings.read(packer.size)
                    bloque_int = packer.unpack(bytes_leidos)[0]
                    str_bits = str(convertir_a_bin(bloque_int))
                    if len(str_bits) < 32:
                        str_bits = "0" * (32 - len(str_bits)) + str_bits
                    pos_posting += len(str_bits)
                    bits_posting += str_bits
                inicio_offset = inicio_posting - offset_posicion
                fin_offset = fin_posting - offset_posicion
                segmento_posting = bits_posting[inicio_offset:fin_offset]
                bits_posting = bits_posting[fin_offset:]
                offset_posicion += len(segmento_posting)
                tiempo_inicio = time.time()
                componentes_posting = decodificar_numeros_vl_str(segmento_posting)
                tiempo_descompresion = time.time() - tiempo_inicio
                self.procesar_tiempo(tipo_compresion, modo_docs, tiempo_descompresion)
                posting = []
                df_termino = componentes_posting[0]
                posting.append(df_termino)
                id_doc_anterior = -1
                for i in xrange(0, df_termino * 2, 2):
                    if modo_docs == self.MODO_NORMAL:
                        id_doc = componentes_posting[i + 1] - 1
                    else:
                        id_doc = (componentes_posting[i + 1]) + id_doc_anterior
                        id_doc_anterior = id_doc
                    tf_termino = componentes_posting[i + 2]
                    posting.append((id_doc, tf_termino))

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
                    file_tiempos.write(u"TIEMPO MÍNIMO DE DESCOMPRESIÓN: " + str(minimo) + " segundos\n")
                    file_tiempos.write(u"TIEMPO MÁXIMO DE DESCOMPRESIÓN: " + str(maximo) + " segundos\n")
                    file_tiempos.write(u"TIEMPO PROMEDIO DE DESCOMPRESIÓN: " + str(promedio) + " segundos\n")
                    file_tiempos.write(u"TIEMPO TOTAL DE DESCOMPRESIÓN: " + str(suma) + " segundos\n")
                    file_tiempos.write("\n")


def main(dir_indices):
    descompresor = DescompresorPostings(dir_indices)
    print u"Usando el tipo de compresión: " + descompresor.TIPO_VLENGTH + "..."
    for modo_docs in [descompresor.MODO_NORMAL, descompresor.MODO_DGAPS]:
        print u"Leyendo los IDs de los documentos en modo: " + modo_docs + "..."
        print u"Cargando el indice..."
        descompresor.cargar_indice(descompresor.TIPO_VLENGTH, modo_docs)
        print u"Descomprimiendo las posting-lists..."
        descompresor.cargar_postings(descompresor.TIPO_VLENGTH, modo_docs)
    print u"Guardando los tiempos de descompresión..."
    descompresor.guardar_tiempos()
    print u"Finalizado!"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print u"ERROR: Debe ingresar el directorio que contiene los indices."
        print u"MODO DE USO: descomprimir_postings.py <path_indices>"
    else:
        main(sys.argv[1])
