#!/usr/bin/python
import MySQLdb

class Database:
	def __init__ (self, username="user4321", password="gryphon", database="comp4321"):
		if (database == None):
			self.db = MySQLdb.connect(host="localhost", user=username, passwd=password)
		else:
			self.db = MySQLdb.connect(host="localhost", user=username, passwd=password, db=database)
		self.cur = self.db.cursor() 
	def query(self,query):
		self.cur.execute(query)
	def close(self):
		self.db.commit()
		self.cur.close()
		self.db.close()