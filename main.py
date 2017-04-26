#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from os.path import *
from controllers.TokenizadorController import *

def tokenizar(path,pathVacias):
    tokenizadorController = TokenizadorController(path,pathVacias = pathVacias)
    tokenizadorController.run()

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

    tokenizar(path,pathVacias)