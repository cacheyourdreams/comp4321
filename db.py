#!/usr/bin/python
import MySQLdb

class Database:
	def __init__ (self, username="user4321", password="gryphon", database="comp4321"):
		if (database == None):
			self.db = MySQLdb.connect(host="127.0.0.1", user=username, passwd=password)
		else:
			self.db = MySQLdb.connect(host="127.0.0.1", user=username, passwd=password, db=database)
		self.cur = self.db.cursor() 
	def query(self,query, parameters=None):
		if (parameters == None):
			self.cur.execute(query)
		else:
			self.cur.execute(query, parameters)
	def rowcount (self):
		return self.cur.rowcount;
	def commit (self):
		self.db.commit()
	def fetchOne(self):
		return self.cur.fetchone()
	def fetchAll (self):
		return self.cur.fetchall()
	def getInsertId (self):
		return self.cur.lastrowid
	def close(self):
		self.db.commit()
		self.cur.close()
		self.db.close()
