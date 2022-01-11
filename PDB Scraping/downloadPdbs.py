#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 10:40:57 2020

This script takes a list of pdb files and downloads them directly
from protein databank website

@author: gloiseau
"""

import requests
import urllib.request
import os
from biopandas.pdb import PandasPdb as pp

#Functions
def is_downloadable(url):
    """
    Does the url contain a downloadable resource
    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True

#Main
#URL for downloading a pdb file from the protein databank
downloads = 'http://files.rcsb.org/download/'
outpdbs = '/exports/gloiseau/mem/'

urls = []
filedirs = []
filenames = []
membrane = []
count = 0
memlist = ''

#open the file that contains the list of pdbs and save them into a vector
with open('/exports/home/gloiseau/mem.txt', 'rt') as protfile:
    for line in protfile:
        membrane.append(line[:4])

#
for string in membrane:
    urls.append(downloads + string + '.pdb')
    filenames.append(outpdbs + string + '.pdb')
    memlist = memlist + ',' + string

brokenpdbs = open('brokenmembranepdbs.txt', 'w')
F = open('memlist.txt', 'w')
F.write(memlist)
F.close()

filenum = 0
for url in urls:
    temp = url
    try:
        if is_downloadable(url) is True:
            urllib.request.urlretrieve(url, filenames[filenum])
        else:
            #print(temp)
            brokenpdbs.write(url)
            brokenpdbs.write('\n')
    except:
        print(temp)
        brokenpdbs.write(temp)
        brokenpdbs.write('\n')
    filenum += 1
    #print(filenum)
brokenpdbs.close()
