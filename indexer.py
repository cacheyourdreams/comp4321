#!/usr/bin/python
import MySQLdb
from db import *

class Indexer:
	def __init__(self):
		self.dbInstance = Database()
		
	
	def getLastCrawlTime (self, url):
		self.dbInstance.commit()
	
	
	def indexDocument (self, url, title, size):
		sql_insert = "INSERT INTO Documents (document_url, document_title, document_size) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE document_title = %s, document_size = %s;"
		sql_select = "SELECT document_id FROM Documents WHERE document_url = %s;"
		self.dbInstance.query(sql_insert, (url,title,size,title,size))
		
		if self.dbInstance.rowcount > 0:
			row = self.dbInstance.fetchOne()
			if (row != None):
				return row[0]
			else:
				self.dbInstance.query(sql_select, (url))
				row = self.dbInstance.fetchOne()
				return row[0]
		else:
			return self.dbInstance.getInsertId()
	
	def indexWords (document_id, word_list):
		for i in range(0, len(word_list)):
			continue
	
	def commit (self):
		self.dbInstance.commit()
		
	def close (self):
		self.dbInstance.close()
		
	