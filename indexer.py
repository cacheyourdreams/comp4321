#!/usr/bin/python
import MySQLdb
from db import *
import sys
sys.path.append("stemming-1.0-py2.5.egg")
from stemming.porter import stem


class Indexer:
	def __init__(self):
		self.dbInstance = Database()
		self.stopwords = set()
		
		with open("stopwords.txt", "r") as ins:
			array = []
			for line in ins:
				self.stopwords.add(line.strip())


	def getLastCrawlTime (self, url):
		self.dbInstance.commit()


	def indexDocument (self, url, title, size, modified = None):
		
		sql_select = "SELECT document_id FROM Documents WHERE document_url = %s;"
		sql_insert = "INSERT INTO Documents (document_url, document_title, document_size) \
		VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE document_title = %s, document_size = %s;"
		placeholders = (url,title,size,title,size)
		if (modified != None):
			sql_insert = "INSERT INTO Documents (document_url, document_title, document_size, modified) \
			VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE document_title = %s, document_size = %s, modified = %s;"
			placeholders = (url,title,size,modified,title,size,modified)
		
		self.dbInstance.query(sql_insert, placeholders)


		if self.dbInstance.rowcount > 1:
			#Already seen this document. Find its id and delete it from Keywords and InvertedIndex

			self.dbInstance.query(sql_select, [url])
			row = self.dbInstance.fetchOne()
			doc_id = row[0]

			#Decrease the document frequency each word in the document by 1
			sql_update = "UPDATE KeyWords INNER JOIN InvertedIndex on KeyWords.word_id = InvertedIndex.word_id \
			 			  SET document_frequency = document_frequency - 1 \
						  WHERE document_id = %s;"
			self.dbInstance.query(sql_update, [doc_id])

			#Delete the document from the InvertedIndex
			sql_delete = "DELETE FROM InvertedIndex WHERE document_id = %s"
			self.dbInstance.query(sql_delete, [doc_id])
			
			sql_delete = "DELETE FROM Links WHERE parent_id = %s"
			self.dbInstance.query(sql_delete, [doc_id])

			
			return doc_id

		else:  #If the row was inserted, return its id
			return self.dbInstance.getInsertId()


	def indexLinks (self, parent_id, children):
		for child_id in children:
			sql_insert = "INSERT INTO Links (parent_id, child_url) VALUE (%s, %s) ON DUPLICATE KEY UPDATE parent_id=parent_id;"
			self.dbInstance.query(sql_insert, [parent_id, child_id])

	def indexWords (self,document_id, word_list, title_word_list):
		term_frequency = {}
		positions = {}
		max_tf = 1
		
		p = 0
		for i in range(0, len(word_list)):
			word = word_list[i].lower()
			#stop word removal
			if self.isStopword(word):
				continue
			#stemming
			word = self.getStemmed(word);
			
			if term_frequency.has_key(word):
				term_frequency[word] += 1
				if term_frequency[word] > max_tf:
					max_tf = term_frequency[word]
			else:
				term_frequency[word] = 1
				
			if positions.has_key(word):
				positions[word].append(p)
			else:
				positions[word] = [p]
			p = p + 1
		
		wordIds = {}
		for word in term_frequency:
			word_id = self.addToKeywords(word)
			wordIds[word] = word_id
			in_title = 0
			if (word in title_word_list):
				in_title = 1
			self.addToInvertedIndex(word_id,document_id,term_frequency[word],in_title)

		self.addToIndexPositions(positions,document_id,wordIds)
		
		#update maximum term frequency figure
		sql_update = "UPDATE Documents SET max_tf=%s WHERE document_id=%s;"
		self.dbInstance.query(sql_update,(max_tf,document_id))
		return len(term_frequency)
	
	def isStopword(self, word):
		return (word in self.stopwords)
	
	def getStemmed (self, word):
		return stem(word)
		
	def addToIndexPositions(self,positions,d,wordIds):
		for w in positions.keys():
			for p in positions[w]:
				sql_insert = "INSERT INTO IndexPositions (word_id, document_id, position) \
		VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE position=position;"
				self.dbInstance.query(sql_insert,(wordIds[w],d,p))


	def addToInvertedIndex(self,wrd_id,doc_id,term_freq,in_title):
		sql_insert = "INSERT INTO InvertedIndex (word_id, document_id,term_frequency,in_title) \
		VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE term_frequency=%s;"
		self.dbInstance.query(sql_insert,(wrd_id,doc_id,term_freq,term_freq,in_title))

	def addToKeywords(self,word):

		sql_insert = "INSERT INTO KeyWords (word, document_frequency) \
		VALUES (%s, 1) ON DUPLICATE KEY UPDATE document_frequency = document_frequency + 1;"

		sql_select = "SELECT word_id FROM KeyWords WHERE word = %s;"

		self.dbInstance.query(sql_insert, [word])
		if self.dbInstance.rowcount > 0:
			row = self.dbInstance.fetchOne()
			if (row != None):
				return row[0]
			else:
				self.dbInstance.query(sql_select, [word])
				row = self.dbInstance.fetchOne()
				return row[0]
		else:
			return self.dbInstance.getInsertId()

	def commit (self):
		self.dbInstance.commit()

	def close (self):
		self.dbInstance.close()
