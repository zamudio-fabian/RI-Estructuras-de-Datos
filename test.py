#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import resource
import sys
import subprocess


        
if __name__ == "__main__":
    soft, hard = resource.getrlimit(resource.RLIMIT_DATA)
    resource.setrlimit(resource.RLIMIT_DATA, (100, hard))
    soft, hard = resource.getrlimit(resource.RLIMIT_MEMLOCK)
    resource.setrlimit(resource.RLIMIT_MEMLOCK, (100, hard))
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (100, hard))
    soft, hard = resource.getrlimit(resource.RLIMIT_DATA)
    print 'Memoria  Maxima Asignada  :', soft, hard
    global filesToIndex, triples
    filesToIndex = range(9999)
    triples = []
    try:
        for index in filesToIndex:
            triples.append('a' * 1000000)
    except Exception as e:
        print "MEMORY ERROR!"
    soft, hard = resource.getrlimit(resource.RLIMIT_DATA)
    print 'Memoria  Maxima Asignada  :', soft, hard
    print len(triples)
    input("Press Enter to continue...")