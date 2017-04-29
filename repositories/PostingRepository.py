#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
from struct import *

class PostingRepository:

    fileNameTerminos = "results/forhumans.txt"
    fileNamePosting = "results/postings.bin"

    def __init__(self):
        pass

    def save(self,terminos):
        with codecs.open(self.fileNameTerminos, mode="w", encoding="utf-8") as archivo:
            index = 0
            archivo.write('ID'.ljust(6))
            archivo.write('|')
            archivo.write('TERMINO'.ljust(30))
            archivo.write('|')
            archivo.write('CF'.ljust(6))
            archivo.write('|')
            archivo.write('DF'.ljust(6))
            archivo.write('\n')
            archivo.write('-'*50)
            archivo.write('\n')
            for termino in sorted(terminos.keys()):
                archivo.write(str(index).ljust(6))
                archivo.write('|')
                archivo.write(termino.ljust(30))
                archivo.write('|')
                archivo.write(str(terminos[termino]['CF']).ljust(6))
                archivo.write('|')
                archivo.write(str(len(terminos[termino]['DOCS'])).ljust(6))
                archivo.write('\n')
                index += 1
            archivo.close()

    def saveBinario(self,terminos):
        lexicon = {}
        lastPosition = 0
        with open(self.fileNamePosting, "wb") as file:
            for terminoKey in sorted(terminos.keys()):
                cantidadDocs = len(terminos[terminoKey]['DOCS'])
                estructura = Struct('i'*cantidadDocs)
                file.write(estructura.pack(*terminos[terminoKey]['DOCS']))
                details = [cantidadDocs,lastPosition]
                lexicon[terminoKey] = details
                lastPosition = lastPosition + estructura.size # 4 bytes ocupa un unsigned int
            file.close()
        return lexicon

    def getPosting(self,inicio,cantidad):
        with open(self.fileNamePosting, "rb") as file:
            file.seek(inicio)
            estructura = Struct('i'*cantidad)
            out = file.read(estructura.size)
            out_unpacked = estructura.unpack(out)
            file.close()
            return out_unpacked
        return lexicon
        
            