#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from os.path import *
from controllers.TokenizadorController import *
from controllers.BooleanQueryController import *

def tokenizar(path,pathVacias):
    tokenizadorController = TokenizadorController(path,pathVacias = pathVacias)
    return tokenizadorController.run()

if __name__ == "__main__":
    if (len(sys.argv) <= 1):
        sys.exit("Error. Faltan parametros")

    directory = sys.argv[1]
    path = relpath(directory)

    if(len(sys.argv) > 2):
        pathVacias = relpath(sys.argv[2])
    else:
        pathVacias = None

    if (isdir(path) == 0):
        sys.exit("Error. No existe el directorio")

    response = tokenizar(path,pathVacias)
    booleanQueryController = BooleanQueryController()
    booleanQueryController.setParams(response)

    
    query = raw_input('Ingrese su búsqueda booleana (exit para salir): ').decode('UTF-8')
    while query != u'exit':
        print booleanQueryController.getResults(query)
        query = raw_input('Ingrese su búsqueda booleana: ').decode('UTF-8')



