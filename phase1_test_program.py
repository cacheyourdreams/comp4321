#!/usr/bin/python
import MySQLdb
from db import *


dbconn = Database()

sql_select = "SELECT document_id, document_title, document_url, modified, document_size FROM Documents;"
dbconn.query(sql_select)

docs = dbconn.fetchAll()

for doc in docs:
	print doc[1]
	print doc[2]
	print doc[3], ",", doc[4]
	
	sql_select = "SELECT word, term_frequency FROM InvertedIndex LEFT JOIN KeyWords on KeyWords.word_id = InvertedIndex.word_id WHERE InvertedIndex.document_id = %s ORDER BY term_frequency DESC;"
	dbconn.query(sql_select, doc[0])
	words = dbconn.fetchAll()
	for word in words:
		print word[0], word[1], ";",
	print ""
	
	sql_select = "SELECT child_url FROM Links WHERE Links.parent_id = %s;"
	dbconn.query(sql_select, doc[0])
	children = dbconn.fetchAll()
	for child in children:
		print "Child", child[0]
	
	print "-------------------------------------------------------------------------------------------"
	

