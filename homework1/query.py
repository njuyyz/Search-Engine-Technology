#!/usr/bin/python

import cPickle as pickle
from stemming.porter2 import stem
import sqlite3
import re
import shlex, time, tarfile
from subprocess import call

# For the df command.
# return the document frequency of a single phrase or word.
def df(text,index):
	text = text.strip()

	# If text is a phrase, split it and get a words list.
	# If test is a word, do as phrase, but nothing will change. 
	textList = re.split('\W+',text)
	if len(textList) > 0:

		# Stem the words in the textList
		textList = [stem(word) for word in textList]
		setList = list()
		length = len(textList)-1
		for word in textList:

			if index.has_key(word)==False:
				print 0
				return

			# Record the words as (docNo, location+length) 
			# (location + length) will make the second number in such tuple be the same
			# if the words in textList showing up in the right order.
			wordSet = { (tuples[0], tuples[1]+length) for tuples in index[word]}
			setList.append(wordSet)
			length-=1
		docNum= setList[0]

		# Doing 'And' for all the set, and get a set of tuple for the whole phrase showing up together. 
		for Docset in setList:
			docNum = docNum & Docset

		# docFinal record the id of the documents which contain the phrase.
		docFinal = set()
		for dn in docNum:
			docFinal.add(dn[0])
		print len(docFinal)

# For the 'freq' command
# similar to the 'df' command except for removing the last step.
def freq(text,index):
	text = text.strip()
	textList = re.split('\W+',text)
	if len(textList) > 1:
		textList = [stem(word) for word in textList]
		setList = list()
		length = len(textList)-1
		for word in textList:

			if index.has_key(word)==False:
				print 0
				return
			wordSet = { (tuples[0], tuples[1]+length) for tuples in index[word]}
			setList.append(wordSet)
			length-=1
		docNum= setList[0]
		for Docset in setList:
			docNum = docNum & Docset
		print len(docNum)

	else:
		text = stem(textList[0])
		if index.has_key(text)==False:
			print 0
			return
		print len(index[text])

# Read the term frequency from the index file and print it.
def termFreq(doc_no,word,tf):
	try:
		doc_no = int(doc_no)
		if tf.has_key(doc_no) ==False:
			print "File "+doc_no+' does not exist.'
			return
		doc_tf = tf[doc_no]
		if doc_tf.has_key(word) == False:
			print 0
			return
		number = doc_tf[word]
		print number
	except ValueError:
		print "File "+doc_no+' does not exist.'

# For 'title' command
def showTitle(doc_no):
	con = sqlite3.connect('./mydb.db3')
	cur = con.cursor()
	cur.execute('select title from document where did=%s'%doc_no)
	con.commit()
	data = cur.fetchall()
	if len(data) == 0:
		print "file "+doc_no+" does not exist"
	else:
		print (data[0][0]).encode('ascii','ignore')
	con.close()

# Calculate the edit distance of 2 words
def levenshtein(seq1, seq2):
    oneago = None
    thisrow = range(1, len(seq2) + 1) + [0]
    for x in xrange(len(seq1)):
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in xrange(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
    return thisrow[len(seq2) - 1]

# For 'similar' command.
# Find the similar words for the input word.
# Similar words is the words which have edit distance less than 3 from input word.
def findSimilar(word,index):
	similarList = list()
	startTime = time.time()
	for key in index.keys():
		if levenshtein(word,key) < 3:
			similarList.append(key)
	end_time = time.time()-startTime
	for find in similarList:
		print find,",",

	print "\ntotal time for finding similar words \033[92m%.5f\033[0ms"%end_time

#Find the documents that do not contain word,
#set the score of these document to 0
def findNegate(word, score,index):
	word = word.strip()
	wordList = re.split('\W+',word);
	textList = filter(None, wordList)
	docFinal = set()

	textList = [stem(word) for word in textList]
	setList = list()
	length = len(textList)-1
	for word in textList:

		if index.has_key(word)==False:
			setList = None
			break
		wordSet = { (tuples[0], tuples[1]+length) for tuples in index[word]}
		setList.append(wordSet)
		length-=1
	docNum = set()
	if setList == None:
		docNum = set()
	else:
		docNum= setList[0]
		for Docset in setList:
			docNum = docNum & Docset
	
	for dn in docNum:
		docFinal.add(dn[0])

	con = sqlite3.connect('./mydb.db3')
	cur = con.cursor()
	cur.execute('select did from document')
	con.commit()
	targetDoc = set()
	for row in cur:
		targetDoc.add(row[0])
	con.close()

	targetDoc -=docFinal
	for item in targetDoc:
		if score.has_key(item):
			score[item] += 1
			continue
		else:
			score[item] = 1
	return targetDoc

def findPostive(word,score,index):
	word = word.strip()
	wordList = re.split('\W+',word);
	textList = filter(None, wordList)

	docFinal = set()

	textList = [stem(word) for word in textList]
	setList = list()
	length = len(textList)-1
	for word in textList:
		if index.has_key(word)==False:
			return
		wordSet = { (tuples[0], tuples[1]+length) for tuples in index[word]}
		setList.append(wordSet)
		length-=1
	docNum= setList[0]
	for Docset in setList:
		docNum = docNum & Docset
	for item in docNum:
		if score.has_key(item[0]):
			score[item[0]]+= len(textList)
		else:
			score[item[0]] = len(textList)
	targetDoc = dict()
	for doc in docNum:
		if targetDoc.has_key(doc[0]):
			continue
		targetDoc[doc[0]] = (doc[1]-len(textList)+1,len(textList))
	return targetDoc

def removeNewLine(s):
	while '\n' in s:
		s = s.replace('\n',' ')
	return s

# Search a word or phrase with index. 
def search(words, wordLoc,index):

	totalTime = 0
	score = dict()
	doc_find = dict()
	startTime = time.time()
	for word in words:
		if word[0] == '!':
			negateWord = findNegate(word[1:],score,index)
		else:
			positiveWord = findPostive(word,score,index)
			if positiveWord == None:
				continue
			for doc in positiveWord.keys():
				if doc_find.has_key(doc):
					continue
				doc_find[doc] = positiveWord[doc]

	# No documents found.
	if score == {}:
		print "\033[91m[SORRY] No file contains these phrases\033[0m"
		return
	# Record the running time for searching.
	totalTime += time.time() - startTime
	con = sqlite3.connect('./mydb.db3')
	cur = con.cursor()

	# get the sentences of the documents, which contain aimed words or phrase.
	for doc in sorted(score,key=score.get,reverse=True):
		segmentTime = time.time()
		doc_no = doc
		word_seq = 1
		word_length = 5
		if doc_find.has_key(doc):
			word_seq = doc_find[doc][0]
			word_length = doc_find[doc][1]
		else:
			word_length = 0

		doc_search_in = wordLoc[doc_no]
		

		#the target phrase start location
		word_loc = doc_search_in[word_seq]
		i = 5
		start = 3
		while True:
			if doc_search_in.has_key(word_seq-start):
				break
			else:
				start -= 1
		tempLength = word_length
		while  True:
			if doc_search_in.has_key(word_seq+tempLength):
				break
			else:
				tempLength -= 1

		end = 3+tempLength
		while True:
			if doc_search_in.has_key(word_seq+end):
				break
			else:
				end -= 1
		word_start = doc_search_in[word_seq-start]
		word_median = doc_search_in[word_seq+tempLength]
		word_end = doc_search_in[word_seq+end]
		flag = False
		if word_length > tempLength:
			flag = True

		#print "score:"+str(score[doc])
		#print "word_length:" + str(word_length)
		#print "word start:"+str(word_start)
		#print "word loc :" + str(word_loc)
		#print "word median: "+str(word_median)
		#print "word end: "+ str(word_end)
		totalTime += time.time() - segmentTime
		try:
			cur.execute('select content from document where did='+str(doc_no))
		except:
			errInfo()
			con.close()
			return
		for row in cur:
			content = row[0]
			print '\033[92m'+"%04d"%doc_no+' [score:%d]:\033[0m'%score[doc],
			if not word_start == 0:
				print '...', 
			start_sentence  = ''
			if not word_loc ==0:
				s = content[word_start:word_loc]
				s = removeNewLine(s)
				start_sentence = s

			if word_start == word_end:
				x = content
				x = removeNewLine(x)
				if word_length == 0:
					print start_sentence+x,
				else:
					print start_sentence+'\033[93m'+x+'\033[0m',
			elif word_median == word_loc and word_end == word_median:
				s = content[word_loc:]
				s = removeNewLine(s)
				print start_sentence+'\033[93m'+s+'\033[0m',
			elif word_median > word_loc and word_end>word_median:
				s = content[word_loc:word_median]
				s = removeNewLine(s)
				x = content[word_median:word_end]
				x = removeNewLine(x)
				print start_sentence+'\033[93m'+s+'\033[0m'+x,
			elif word_median > word_loc and word_end == word_median and flag == False:
				s = content[word_loc:word_median]
				s = removeNewLine(s)
				x = content[word_median:]
				x = removeNewLine(x)
				print start_sentence+'\033[93m'+s+'\033[0m'+x,
			elif flag == True:
				s = content[word_loc:]
				s = removeNewLine(s)
				print start_sentence+'\033[93m'+s+'\033[0m',
			else:
				s = content[word_start:word_end]
				s = removeNewLine(s)
				print start_sentence+s,
			if not word_end == word_median:
				print '...'
			else:
				print

			break;
	print "total time for searching \033[92m%.5f\033[0ms"%totalTime



def showDoc(docNo):
	con = sqlite3.connect('./mydb.db3')
	cur = con.cursor()
	try:
		cur.execute('select * from document where did=%s'%docNo)
	except:
		errInfo()
		con.close()
		return
	con.commit()
	for text in cur:
		print "\033[93m<DOC_NO>\033[0m"
		print text[0]
		print "\033[93m</DOC_NO>\n<DOC_TITLE>\033[0m"
		print text[1]
		print "\033[93m</DOC_TITLE>\n<DOC_AUTHOR>\033[0m"
		print text[2]
		print "\033[93m</DOC_AUTHOR>\n<DOC_BIBLIO>\033[0m"
		print text[3]
		print "\033[93m</DOC_BIBLIO>\n<DOC_TEXT>\033[0m"
		print text[4]
		print "\033[93m</DOC_TEXT>\033[0m"
	con.close()

def errInfo():
	print '\n\033[91mERROR. Please check the format\033[m\n\n\
	\033[93m df [word]\033[m : shows the number of documents in which [word] appears\n\
	\n\
	\033[93m freq [word]\033[0m : shows how many times the phrase [word] appears in the index\n\
	\n\
	\033[93m doc [doc_no]\033[0m : shows the full text of document [do_no]\n\
	\n\
	\033[93m tf [doc_no] [word]\033[0m : shows the term frequency of [word] in document [doc_no]\n\
	\n\
	\033[93m title [doc_no]\033[0m : shows the title of document [doc_no]\n\
	\n\
	\033[93m similar [word]\033[0m : shows similar words of [word]\n\
	\n\
	\033[93m exit\033[0m : exit the query system\n\n\n'


# Main process begin.
print "initialize query system, please wait :)"
initial_time = time.time()

# Read the index from the pickle file.
tar = tarfile.open("index.tar.gz", "r:gz")
f = tar.extractall()
f = open('index.my','rb')
index = pickle.load(f)
df_list = pickle.load(f)
tf  = pickle.load(f)
wordLoc = pickle.load(f)
print "\ninitialize system successfully!\n"
print "total time for initializing \033[92m%.2f\033[0ms\n\n"%(time.time() - initial_time)

# Loop to get the input of user.
while True:
	try:
		var = raw_input('please search everything you want->')
		t = time.time()
		argv = shlex.split(var.lower())
		if argv[0] == 'df':
			if (len(argv) != 2):
				errInfo()
				continue

			df(argv[1],index)

		elif argv[0] == 'doc':
			if (len(argv) != 2):
				errInfo()
				continue

			showDoc(argv[1])

		elif argv[0] == 'title':
			if (len(argv) != 2):
				errInfo()
				continue

			showTitle(argv[1])

		elif argv[0] == 'tf':
			if (len(argv) != 3):
				errInfo()
				continue

			termFreq(argv[1],argv[2],tf)

		elif argv[0] == 'freq':
			if (len(argv) != 2):
				errInfo()
				continue

			freq(argv[1],index)
		elif argv[0] == 'similar':
			if (len(argv) != 2):
				errInfo()
				continue
			findSimilar(argv[1],index)

		elif argv[0] == 'exit':
			break
		else:
			search(argv,wordLoc,index)
			print "total time for searching and print \033[92m%.5f\033[0ms"%(time.time()-t)
	except :
		errInfo()