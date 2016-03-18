#!/usr/bin/python
import MySQLdb
from db import *

class Indexer:
	def __init__(self):
		self.dbInstance = Database()


	def getLastCrawlTime (self, url):
		self.dbInstance.commit()


	def indexDocument (self, url, title, size):
		sql_insert = "INSERT INTO Documents (document_url, document_title, document_size) \
		VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE document_title = %s, document_size = %s;"
		sql_select = "SELECT document_id FROM Documents WHERE document_url = %s;"
		self.dbInstance.query(sql_insert, (url,title,size,title,size))


		if self.dbInstance.rowcount > 0:
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

			return doc_id

		else:  #If the row was inserted, return its id
			return self.dbInstance.getInsertId()




	def indexWords (self,document_id, word_list):
		term_frequency = {}
		for i in range(0, len(word_list)):
			word = word_list[i].lower()
			if term_frequency.has_key(word):
				term_frequency[word] += 1
			else:
				term_frequency[word] = 1

		for word in term_frequency:
			word_id = self.addToKeywords(word)
			self.addToInvertedIndex(word_id,document_id,term_frequency[word])

		return len(term_frequency)

	def addToInvertedIndex(self,wrd_id,doc_id,term_freq):
		sql_insert = "INSERT INTO InvertedIndex (word_id, document_id,term_frequency) \
		VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE term_frequency=%s;"
		self.dbInstance.query(sql_insert,(wrd_id,doc_id,term_freq,term_freq))

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
