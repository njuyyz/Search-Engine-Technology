#!/usr/bin/python
import csv, string, HTMLParser, pickle,re
from stemming.porter import stem

class Document:

	def __init__(self):
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
		self.pos_count = 0.0
		self.neg_count = 0.0
		for line in csv_file:
			review = line['Review']
			category  =line['Category']
			words = re.split('[^A-Za-z0-9_\']+',review)
			words = filter(None,words)
			words = [stem(word.lower()) for word in words]
			words = set(words)
			if category == '1':

				self.pos_count +=1.0
				for word in words:
					if word == '\'':
						continue
					if self.positive.has_key(word):
						self.positive[word] += 1
					else:
						self.positive[word] = 1
			elif category == '0':
				
				self.neg_count += 1.0
				for word in words:
					if word == '\'':
						continue
					if self.negative.has_key(word):
						self.negative[word] += 1
					else:
						self.negative[word] = 1
		inter_words = set(self.positive.keys())&set(self.negative.keys())
		for word in self.positive.keys():
			self.positive[word] = self.positive[word]/self.pos_count
		for word in self.negative.keys():
			self.negative[word] = self.negative[word]/self.neg_count
		#for word in inter_words:
		#	temp = self.positive[word] - self.negative[word]
		#	if temp < 0 :
		#		del self.positive[word]
		#		self.negative[word] = 0 - temp
		#	else:
		#		del self.negative[word]
		#		self.positive[word] = temp

	def printPos(self):
		for word in sorted(self.negative,key=self.negative.get):
			print "%s 	: 	%f"%(word,self.negative[word])
		print len(self.negative.keys())

	def getP(self, review):
		words = re.split('[^A-Za-z0-9_\']+',review)
		words = filter(None,words)
		words = [stem(word.lower()) for word in words]
		words = set(words)

		pos = (0.0+self.pos_count)/(self.pos_count+self.neg_count)
		for word in words:
			if word in self.positive:
				pos *= self.positive[word]
			else:
				pos *= (1.0/self.pos_count)
		neg = (0.0+self.neg_count)/(self.pos_count+self.neg_count)
		for word in words:
			if word in self.negative:
				neg *= self.negative[word]
			else:
				neg *= (1.0/self.neg_count)

		print "pos:"+str(pos)
		print "neg:"+str(neg)
		if pos > neg:
			return 1
		else:
			return 0




doc = Document()

doc.read_csv_file('../train.csv')
#doc.printPos();
doc.read_test_csv('../test.csv')