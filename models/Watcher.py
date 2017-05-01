#!/usr/bin/env python
# -*- coding: utf-8 -*-
from watchdog.events import PatternMatchingEventHandler  
from controllers.TokenizadorController import *

class Watcher(PatternMatchingEventHandler):
    patterns = ["*.txt"]
    tokenizadorController = None

    def on_modified(self, event):
        response = self.tokenizadorController.run()

    def addTokenizador(self,tokenizadorController):
        self.tokenizadorController = tokenizadorController

        
