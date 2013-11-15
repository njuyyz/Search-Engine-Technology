#!/usr/bin/python
#filename: Document.py
import sqlite3
import xml.etree.ElementTree as et
import re
from stemming.porter2 import stem
import time

class Document:


    '''
        Handle documents. including reading documents, parsing documents,

        splitting documents and buildTF for each document.

    '''
    
    def __init__(self,filename):
        try:
            self.filename = filename
            self.parseFile()
            self.splitDocument()
            self.trackLoc()
            self.buildTF()
        except:
            print "input file format error, please check it"

    # parse documents as xml files. and get the attributes of every single document.
    def parseFile(self):
        try:
            tree = et.parse(self.filename)
            doc = tree.getroot()
            self.docNo = int(doc.find('DOCNO').text)
            self.docTitle = doc.find('TITLE').text
            self.docTitle = self.docTitle.strip()
            self.docAuthor = doc.find('AUTHOR').text
            self.docAuthor = self.docAuthor.strip()
            self.docBiblio = doc.find('BIBLIO').text
            self.docBiblio = self.docBiblio.strip()
            self.docText = doc.find('TEXT').text
            self.docText = self.docText.strip()
        except:
            print "input file format error, please check it"

    # Split documents by comon, space, etc. 
    # And get words, lowcase the words, and stem them.
    def splitDocument(self):
        self.words = re.split('\W+',self.docText)
        self.words = filter(None,self.words)
        self.words = [stem(word.lower()) for word in self.words]

    # Record the offset of each word in a document.
    def trackLoc(self):
        pre = ' '
        loc = 0
        word = 1
        self.wordLoc = dict()
        for c in self.docText:
            if (re.match('\w',c,0) and not re.match('\w',pre,0)):
                self.wordLoc[word] = loc
                word +=1
            loc+=1
            pre = c

    # Build TF (term frequency ) for each word in each document. 
    def buildTF(self):
        self.TF = dict()
        for word in self.words:
            if(self.TF.has_key(word)):
                self.TF[word] += 1
            else:
                self.TF[word] = 1
        return self.TF

    # Store the document in to a database.
    def write2DB(self,cu):
        cu.execute('''insert into document values( %d,"%s","%s","%s","%s")'''%(self.docNo,self.docTitle, self.docAuthor, self.docBiblio, self.docText))

