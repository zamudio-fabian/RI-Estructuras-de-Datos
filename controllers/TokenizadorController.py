#!/usr/bin/env python
# -*- coding: utf-8 -*-
from repositories.CorpusRepository import *
from repositories.TokenRepository import *
from repositories.PostingRepository import *
import codecs

class TokenizadorController():

    path = ''
    corpusRepository = None
    tokenRepository = None
    PostingRepository = None
    pathVacias = None
    fileNameEstaditiscas = 'results/estadistiscas.txt'

    def __init__(self,path,**options):
        self.path = path
        self.corpusRepository = CorpusRepository(path)
        self.tokenRepository = TokenRepository()
        self.PostingRepository = PostingRepository()
        self.pathVacias = options.get('pathVacias', None)

    def run(self):
        documentos = self.corpusRepository.getListDocuments()
        # print "PROCESANDO DOCUMENTOS"
        response = self.tokenRepository.tokenizar(documentos,pathVacias = self.pathVacias)
        # Se guarda primero el archivo en ASCII para control y luego el archivo binario
        self.PostingRepository.save(response['terminos'])
        lexicon = self.PostingRepository.saveBinario(response['terminos'])
        result = {'lexicon':lexicon,'documentos':response['docs'],'estadisticas':response['estadisticas']}
        self.saveEstadisticas(response['estadisticas'])
        return result

    def saveEstadisticas(self,estadisticas):
        with codecs.open(self.fileNameEstaditiscas, mode="w", encoding="utf-8") as archivo:
            index = 1
            archivo.write('='*50)
            archivo.write('\n')
            archivo.write('POSTING MIN: '+str(estadisticas['min'])+' Bytes\n')
            archivo.write('POSTING MAX: '+str(estadisticas['max'])+' Bytes\n')
            archivo.write('POSTING AVG: '+str((estadisticas['totalSize']/estadisticas['countDocs']))+' Bytes\n')
            archivo.write('CANT. FILES: '+str(estadisticas['countDocs'])+'\n')
            archivo.write('SIZE FILES:  '+str(estadisticas['totalSize'])+' Bytes\n')
            archivo.write('OVERHEAD:    '+str(estadisticas['overhead'])+' Bytes\n')
            archivo.write('='*50)
            archivo.write('\n')
            archivo.write('ID DOC'.ljust(6))
            archivo.write('|')
            archivo.write('OVERHEAD')
            archivo.write('\n')
            archivo.write('-'*50)
            archivo.write('\n')
            for key in estadisticas['docs'].keys():
                archivo.write(str(key).ljust(6))
                archivo.write('|')
                aux = "%.4f" % estadisticas['docs'][key]
                archivo.write(aux)
                archivo.write('\n')
                index += 1
            archivo.close()


        
