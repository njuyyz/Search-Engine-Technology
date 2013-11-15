#!/usr/bin/python
import csv, string, HTMLParser, pickle,re
from stemming.porter2 import stem
from math import log

# Author Yunzhi Ye
# Subject: Search Engine Technology
# Date: Friday, Nov. 8th, 2013

class Document:

	def __init__(self):
		pass

	#1. read the test file and get the review contents
	#2. then calculate the P(review = negative) and P(review = positve) for each entry
	#3. compare P(review = negative) and P(review = positve) and get the prediction.
	def read_test_csv(self,filename):

		#get the review file
		csv_test = csv.DictReader(open(filename,'rb'), delimiter=',',quotechar='"')

		#create a new csv file to store the prediction
		csv_file = csv.writer(open('result_2.csv','wb'))
		csv_file.writerow(['Id','Category'])

		# for each review in the review file, get the review content, and call the getP() method to get the prediction
		review_id = 0
		for line in csv_test:
			review_id +=1
			review = line['Review']

			# call getP() methods to get the prediction,
			# 1 for positive
			# 0 for negative
			category = self.getP(review)

			# write the prediction to the csv file
			csv_file.writerow([str(review_id),str(category)])

	# user Mutual Information (MI) algorithm to calculate the I(U;C) of each word,
	# sorted the words by its I(U;C), and selete the most useful feature to predict. 
	def selectFeature(self):

		#get all the words shown in the review from both positive review and negative review
		all_words = set(self.positive.keys())|set(self.negative.keys())

		# store I(U;C) in the dict I
		#
		#					postive 	negative
		#				-------------------------
		#		shown	|	N11		|	N10		|
		#				-------------------------
		#	not shown	|	N01		|	N00		|
		#				-------------------------
		#
		#
		self.I = dict()
		for word in all_words:
			N11 = 1
			if self.positive_feature.has_key(word):
				N11 = self.positive_feature[word]
			N10 = 1
			if self.negative_feature.has_key(word):
				N10 = self.negative_feature[word]
			N01 = self.pos_doc - N11
			N00 = self.neg_doc - N10
			N  =self.pos_doc+self.neg_doc
			
			# apply MI algorithm to calculate the I(U;C)
			self.I[word] = N11*1.0/N*log((N*N11)/((N11+N10*1.0)*(N11+N01)))\
			+N01*1.0/N*log((N*N01*1.0)/((N01+N00)*(N11+N01)))\
			+N10*1.0/N*log((N*N10*1.0)/((N11+N10)*(N10+N00)))\
			+N00*1.0/N*log((N*N00*1.0)/((N01+N00)*(N10+N00)))

		# select the features by I(U;C) of each feature
		temp_positive = dict()
		temp_negative = dict()
		i = 0
		for word in sorted(self.I, key=self.I.get,reverse=True):
			i+=1

			# select the most useful i features
			if i > 11060:
				break
			temp_positive[word] = self.positive[word]
			temp_negative[word] = self.negative[word] 
			#print word,self.I[word]
		self.positive = temp_positive
		self.negative = temp_negative


	# handle the '...' which be regarded as a feature.
	def handle_ep(self,review):
		if review[0:5] =='. . .':
			review = review[6:]
		#if review[-5:] =='. . .':
			#review = review[-6:]
		if '. . .' in review:
			review = review.replace('. . .','-e-t-c-')

		return review

	# train the algorithm
	# read the training csv data
	# get the features
	# apply multinomial algorithm
	def read_csv_file(self, filename):

		# read the training data from the csv file
		csv_file = csv.DictReader(open(filename,'r'), delimiter=',',quotechar='"')
		
		#initialize 2 dict to store the positive features and negative features
		self.positive = dict()
		self.negative = dict()

		# count for the number of positive reviews and negative reviews
		self.pos_doc = 0.0
		self.neg_doc = 0.0
		self.positive_feature = dict()
		self.negative_feature = dict()
		for line in csv_file:
			review = line['Review']
			review = self.handle_ep(review)
			category = line['Category']

			# split the words (features) from the entire review
			words = re.split('[^A-Za-z0-9_\'\"?!-]+',review)
			words = filter(None,words)

			# stem the words and convert them to the lowercase
			words = [stem(word.lower()) for word in words]

			# if the category is 1(positive), store the words of the review into the 
			# positive feature dictionary, and increase the number of the entry
			if category == '1':
				print 'postive'
				positive_word_set = set()
				self.pos_doc +=1.0
				for word in words:
					if word == '\'' or word == '\"':
						continue
					positive_word_set.add(word)
					if self.positive.has_key(word):
						self.positive[word] +=1
					else:
						self.positive[word] = 1
				for word in positive_word_set:
					if self.positive_feature.has_key(word):
						self.positive_feature[word] += 1
					else:
						self.positive_feature[word] = 1

			# if the category is 0(negative), store the words of the review into the 
			# negative feature dictionary, and increase the number of the entry
			elif category == '0':
				print 'negative'
				negative_words_set = set()
				self.neg_doc += 1.0
				for word in words:
					if word == '\'' or word == '\"':
						continue
					negative_words_set.add(word)
					if self.negative.has_key(word):
						self.negative[word] += 1
					else:
						self.negative[word] = 1

				for word in negative_words_set:
					if self.negative_feature.has_key(word):
						self.negative_feature[word] += 1
					else:
						self.negative_feature[word] = 1

		# count the total words we saw in the positive reviews
		self.pos_word_count = 0
		for word in self.positive.keys():
			if len(word) == 1 and word != '?' and word != '!':
				del self.positive[word]
				continue
			self.pos_word_count += self.positive[word]

		# count the total words we saw in the negative reviews
		self.neg_word_count = 0
		for word in self.negative.keys():
			if len(word) == 1 and word != '?' and word != '!':
				del self.negative[word]
				continue
			self.neg_word_count += self.negative[word]

		# get all the words( features ) we saw in both positive reviews and negative reviews
		self.all_words = set(self.positive.keys())|set(self.negative.keys())

		#self.pos_word_count *= 100.0
		#self.neg_word_count *= 100.0

		self.postive_words_number = len(set(self.positive.keys()))
		self.negative_words_number = len(set(self.negative.keys()))
		# apply the Multinomial Naive Bayes Algorithms
		for word in self.all_words:
			if word in self.positive.keys():
				self.positive[word] = (self.positive[word]+1.0)/(self.pos_word_count+self.postive_words_number)
			else:
				self.positive[word] = (1.0)/(self.pos_word_count+self.postive_words_number)
			if word in self.negative.keys():
				self.negative[word] = (self.negative[word]+1.0)/(self.neg_word_count+self.negative_words_number)
			else:
				self.negative[word] = 1.0/(self.neg_word_count+self.negative_words_number)

			#if word[-1]=="'":
			#	print word, self.positive[word]/self.negative[word]
		#for word in inter_words:
		#	temp = self.positive[word] - self.negative[word]
		#	if temp < 0 :
		#		del self.positive[word]
		#		self.negative[word] = 0 - temp
		#	else:
		#		del self.negative[word]
		#		self.positive[word] = temp

	# get the probability of being positive and being negative,
	# then campare the two propabilities and predict certain review is positive or negative.
	def getP(self, review):

		# get the features of the review
		review = self.handle_ep(review)
		words = re.split('[^A-Za-z0-9_\'\"?!-]+',review)
		words = filter(None,words)
		words = [stem(word.lower()) for word in words]

		# prior of positive
		pos = (0.0+self.pos_doc)/(self.pos_doc+self.neg_doc)

		# apply naive bayes, and get the probability of being positive 
		for word in words:
			if len(word) == 1 and word != '?' and word != '!':
				continue
			if word in self.positive:
				pos *= self.positive[word]

		# prior of negative
		neg = (0.0+self.neg_doc)/(self.pos_doc+self.neg_doc)

		# apply naive bayes, and get the probability of being negative
		for word in words:
			#print word
			if len(word) == 1 and word != '?' and word != '!':
				continue
			if word in self.negative:
				neg *= self.negative[word]

		#print "pos:"+str(pos)
		#print "neg:"+str(neg)

		# compare the probabilities of being positive and be negative
		if pos >= neg:
			#print 'pos'
			return 1
		else:
			#print 'neg'
			return 0




doc = Document()

# read the training data
# train the system
doc.read_csv_file('../train.csv')

# select the features we will use for testing
doc.selectFeature()

# apply the algorithm to the test data
doc.read_test_csv('../test.csv')










