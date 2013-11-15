#!/usr/bin/python
import csv, string, HTMLParser, pickle,re
from stemming.porter2 import stem

class Document:

	
	def __init__(self):
		self.neg_set = set(["don't","won't","can't","shouldn't","isn't","aren't","doesn't","didn't","haven't","hard","few","little","couldn't"])

		pass

	def read_test_csv(self,filename):
		csv_test = csv.DictReader(open(filename,'rb'), delimiter=',',quotechar='"')

		csv_file = csv.writer(open('result.csv','wb'))
		csv_file.writerow(['Id','Category'])
		review_id = 0
		for line in csv_test:
			review_id +=1
			review = line['Review']
			category = self.getP(review)
			csv_file.writerow([str(review_id),str(category)])



	def read_csv_file(self, filename):
		csv_file = csv.DictReader(open(filename,'rb'), delimiter=',',quotechar='"')
		self.positive = dict()
		#self.pos_alpha = dict()
		self.negative = dict()
		#self.neg_alpha = dict()
		self.pos_doc = 0.0
		self.neg_doc = 0.0
		for line in csv_file:
			review = line['Review']
			category  =line['Category']
			words = re.split('[^A-Za-z0-9_\'\"?!]+',review)
			words = filter(None,words)
			words = [stem(word.lower()) for word in words]
			if category == '1':

				self.pos_doc +=1.0
				former_word = ' '
				for word in words:
					if word == '\'' or word == '\"':
						continue
					if word in self.neg_set:
						former_word = word
						continue
					if former_word in self.neg_set:
						print former_word," ",word
						if self.negative.has_key(word):
							self.negative[word] += 1
						else:
							self.negative[word] = 1
					else:
						if self.positive.has_key(word):
							self.positive[word] +=1
						else:
							self.positive[word] = 1
					former_word = word
			elif category == '0':
				
				self.neg_doc += 1.0
				former_word = ' '
				for word in words:
					if word == '\'' or word == '\"':
						continue
					if word in self.neg_set:
						former_word = word
						continue
					if former_word in self.neg_set:
						print former_word," ",word
						if self.positive.has_key(word):
							self.positive[word] += 1
						else:
							self.positive[word] = 1
					else:
						if self.negative.has_key(word):
							self.negative[word] += 1
						else:
							self.negative[word] = 1
					former_word = word

		self.all_words = set(self.positive.keys())|set(self.negative.keys())

		self.pos_word_count = 0
		for word in self.positive.keys():
			if len(word) == 1 and word != '?' and word != '!':
				del self.positive[word]
				continue
			self.pos_word_count += self.positive[word]

		self.neg_word_count = 0
		for word in self.negative.keys():
			if len(word) == 1 and word != '?' and word != '!':
				del self.negative[word]
				continue
			self.neg_word_count += self.negative[word]

		self.pos_word_count *= 100.0
		self.neg_word_count *= 100.0
		self.postive_words_number = len(set(self.positive.keys()))
		self.negative_words_number = len(set(self.negative.keys()))

		print "sick",self.positive['sick'],self.negative['sick']
		for word in self.all_words:

			if word in self.positive.keys():
				self.positive[word] = (self.positive[word]+1.0)/(self.pos_word_count+self.postive_words_number)
			else:
				self.positive[word] = (1.0)/(self.pos_word_count+self.postive_words_number)
			if word in self.negative.keys():
				self.negative[word] = (self.negative[word]+1.0)/(self.neg_word_count+self.negative_words_number)
			else:
				self.negative[word] = 1.0/(self.neg_word_count+self.negative_words_number)

			#print word, "pos/neg: ", self.positive[word]/self.negative[word]
		#for word in inter_words:
		#	temp = self.positive[word] - self.negative[word]
		#	if temp < 0 :
		#		del self.positive[word]
		#		self.negative[word] = 0 - temp
		#	else:
		#		del self.negative[word]
		#		self.positive[word] = temp

	def printPos(self):
		pass

	def getP(self, review):
		words = re.split('[^A-Za-z0-9_\'\"?!]+',review)
		words = filter(None,words)
		words = [stem(word.lower()) for word in words]

		pos = (0.0+self.pos_doc)/(self.pos_doc+self.neg_doc)
		former_word = ' '
		for word in words:

			if len(word) == 1 and word != '?' and word != '!':
				continue
			if word in self.neg_set:
				former_word = word
				continue
			if former_word in self.neg_set:
				if word in self.negative:
					pos *= self.negative[word]
			elif word in self.positive:
				pos *= self.positive[word]
			former_word = word
		
		neg = (0.0+self.neg_doc)/(self.pos_doc+self.neg_doc)
		former_word = ' '
		for word in words:

			if len(word) == 1 and word != '?' and word != '!':
				continue
			if word in self.neg_set:
				former_word = word
				continue
			if former_word in self.neg_set:
				if word in self.positive:
					neg *= self.positive[word]
			elif word in self.negative:
				neg *= self.negative[word]
			former_word = word

		#print "pos:"+str(pos)
		#print "neg:"+str(neg)
		if pos > neg:
			#print 'pos'
			return 1
		else:
			#print 'neg'
			return 0




doc = Document()

doc.read_csv_file('../train.csv')
doc.printPos();
doc.read_test_csv('../test.csv')