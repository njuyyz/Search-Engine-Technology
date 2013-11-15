#!/usr/bin/python
#filename: IDF.py

from Document import Document
from os import walk, sep, system
from math import log
import sqlite3
import time

class IDF:


	''' 

	From the filePath to read all the files.

	Then calculate their DF, TF, IDF

	'''

	def __init__(self, filePath):
		self.filePath = filePath
		self.DF = dict()
		self.doc_count = 0;
		self.getFiles()


	def getFiles(self):
		self.files = []
		for (dirpath, dirnames, filenames) in walk(self.filePath):
			self.files.extend([dirpath + sep + filename for filename in filenames])
		self.doc_count = len(self.files)
		return self.files

		
	def buildDF(self,doc):
		for k in doc.TF.keys():
			if self.DF.has_key(k):
				self.DF[k] += 1
			else:
				self.DF[k] = 1

		return self.DF

	def buildIDF(self):
		self.freqList = dict()
		if self.DF == None:
			self.buildDF()
		for k in self.DF.keys():
			v = self.DF[k]
			frequency = log(self.doc_count/float(v))
			self.freqList[k] = (v,frequency)

		return self.freqList
