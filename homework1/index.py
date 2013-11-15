#!/usr/bin/python

from Document import Document
import cPickle as pickle
from IDF import IDF
from os import system
import sqlite3
import time
import sys, os, tarfile, math


class Index:


	'''build up invert Index'''

	def __init__(self):
		self.wordList = dict()
		self.numDoc = 0
		pass


	def buildIndex(self, doc):
		self.numDoc += 1
		docNo = int(doc.docNo)
		words = doc.words
		loc= 1
		for word in words:
			item = (docNo, loc)
			if self.wordList.has_key(word):
				self.wordList[word].append(item)
			else:
				itemList = [item]
				self.wordList[word] = itemList
			loc+=1

	def seldomWords(self):
		self.seldomWordsList = dict()
		for word in self.wordList.keys():
			if len(word) < 20:
				self.seldomWordsList[word] = self.wordList[word]

	def wordsVector(self):
		self.documentList = [[0 for x in range(len(self.seldomWordsList.keys()))] for y in range(self.numDoc)]
		i=-1
		for word in self.seldomWordsList.keys():
			i += 1
			for (docNo,loc) in self.seldomWordsList[word]:
				self.documentList[docNo][i] = 1

	def cosineSimilarity(self):
		self.cosinePair = [[0 for x in range(self.numDoc)] for y in range(self.numDoc)]
		self.documentLength = [0 for x in range(self.numDoc)]

		for m in range(self.numDoc):
			sums = 0
			for s in range(len(self.seldomWordsList.keys())):
				sums = sums + self.documentList[m][s]
			self.documentLength[m] = math.sqrt(sums)

		for i in range(self.numDoc):
			print i
			for j in xrange(i+1, self.numDoc):
				sums = 0
				for k in range(len(self.seldomWordsList.keys())):
					sums = sums + self.documentList[i][k]*self.documentList[j][k]

				self.cosinePair[i][j] = float(1.0+sums)/float(1.0+self.documentLength[i]*self.documentLength[j])

				if self.cosinePair[i][j] > 0.7:
					print "doc: %d, doc: %d : %f"%(i,j,self.cosinePair[i][j])




# Start Indexing all the documents
print "start indexing..."

# If mydb.db3 file already exists, delete it, 
# and create a new mydb.db3 file to setup database 
system("rm ./mydb.db3")
con = sqlite3.connect('./mydb.db3')
cur = con.cursor()
cur.execute('CREATE TABLE document(\
			did INTEGER PRIMARY KEY, title VARCHAR(100),\
			author VARCHAR(100), biblio VARCHAR(200),\
			content VARCHAR(9999999))')
con.commit()

# startTime record the start time of indexing process.
startTime = time.time()
idf = IDF(sys.argv[1])
index = Index()
i = 1
size = len(idf.files)
tf = dict()
wordLoc = dict()

# Index files 
t = 0
for f in idf.files:
    try:
	    temp = time.time()
	    doc = Document(f)
	    index.buildIndex(doc)
	    tf[doc.docNo] = doc.TF
	    wordLoc[doc.docNo] = doc.wordLoc
	    idf.buildDF(doc)
	    t=t + (time.time()-temp)
	    doc.write2DB(cur)
	    i +=1
	    if i%10==0:
	    	if i%300==0:
	    		con.commit()
	    	percent = i*100/size
	    	t = time.time() - startTime
	    	sys.stdout.write('\r indexing...\033[92m%2d\033[0m%%   \033[92m%2.0f\033[0ms'%(percent,t))
	    	sys.stdout.flush()
    except:
        print " some file format is not correct!"
        continue
con.commit()
idf.buildIDF()
#index.seldomWords()
#index.wordsVector()
#index.cosineSimilarity()
print "\n\n\n\rindex complete!\n"
print "total index time : \033[92m%3.2f\033[0ms"%t

# Store the index in a pickle file
indexStore = open('index.my','wb')
pickle.dump(index.wordList,indexStore,0)
pickle.dump(idf.DF,indexStore,0)
pickle.dump(tf,indexStore,0)
pickle.dump(wordLoc,indexStore,0)
indexStore.close()

# Compress the pickle file into a tar.gz file
print "start compressing the index"
compressTime = time.time()
tar = tarfile.open("index.tar.gz","w:gz")
tar.add('index.my','index.my')
tar.close()

# Remove the original pickle file
os.remove('index.my')
print "compress complete"

# Print out the time for compressing index file
print "total time to compress %.0fs"%(time.time()-compressTime)

# Present the statistics of the compressed index file
fileStats = os.stat('index.tar.gz')
fileSize = fileStats.st_size
fileSize = fileSize/1024
print "total index size : \033[92m%.0f\033[0mKB"%fileSize
