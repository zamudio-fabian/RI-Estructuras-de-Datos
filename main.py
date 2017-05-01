#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from os.path import *
from controllers.TokenizadorController import *
from controllers.BooleanQueryController import *
import time  
from watchdog.observers import Observer  
from models.Watcher import *



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

    
    tokenizadorController = TokenizadorController(path,pathVacias = pathVacias)
    response = tokenizadorController.run()

    booleanQueryController = BooleanQueryController()
    booleanQueryController.setParams(response)

    myWatcher = Watcher()
    myWatcher.addTokenizador(tokenizadorController)
    
    observer = Observer()
    observer.schedule(myWatcher, path)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()



