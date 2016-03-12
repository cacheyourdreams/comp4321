#!/usr/bin/python
import MySQLdb

class Database:
	def __init__(self):
		self.db = MySQLdb.connect(host="localhost", user="user4321", passwd="gryphon", db="comp4321")
		self.cur = self.db.cursor() 
	def query(self,query):
		self.cur.execute(query)