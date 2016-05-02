#!/usr/bin/python
import MySQLdb #mySQL
from db import Database
from getpass import getpass
import sys

def main():
	print "database structure will be created, any exising database/user WILL BE DROPPED"
	print "enter mysql root username (leave blank for \"root\"):"
	username = raw_input()
	password = getpass()
	if username == "" or username == None:
		username = "root"
	try:
		conn = Database(username, password, database=None)
	except:
		print "error connecting to mysql database as root"
		sys.exit(1)
	conn.query("DROP DATABASE IF EXISTS comp4321;")
	conn.query("GRANT USAGE ON *.* TO 'user4321'@'localhost';")
	conn.query("DROP USER 'user4321'@'localhost';")

	conn.query("CREATE DATABASE comp4321;")
	conn.query("GRANT ALL PRIVILEGES ON comp4321.* To 'user4321'@'localhost' IDENTIFIED BY 'gryphon';")

	conn.close()

	userConn = Database()

	userConn.query("CREATE TABLE Documents (\
	document_id int NOT NULL AUTO_INCREMENT,\
	document_url varchar(255) NOT NULL,\
	document_title varchar(255) NOT NULL,\
	document_size int NOT NULL,\
	modified DATETIME,\
	fetched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
	max_tf int DEFAULT 1,\
	PRIMARY KEY (document_id),\
	UNIQUE (document_url),\
	INDEX url_index (document_url));")

	userConn.query("CREATE TABLE Links (\
	parent_id int NOT NULL,\
	child_url varchar(255) NOT NULL,\
	PRIMARY KEY (parent_id, child_url),\
	FOREIGN KEY (parent_id) REFERENCES Documents(document_id) ON DELETE CASCADE\
	);")
#FOREIGN KEY (child_id) REFERENCES Documents(document_id) ON DELETE CASCADE
#disabled this constraint for the time being, to allow links to children which have not yet been scraped. Eventually it may be bettter to add this back in and add rows to Links when processing the child document instead of the parent document (would require keeping track of which document adds pages to the scrape queue)
#also this would allow child_url to become child_id again

#eventually include idf in this table
	userConn.query("CREATE TABLE KeyWords (\
	word_id	int NOT NULL AUTO_INCREMENT,\
	word VARCHAR(255) NOT NULL,\
	document_frequency int NOT NULL COMMENT 'the number of unique documents which contain at least one instance of the word',\
	PRIMARY KEY (word_id),\
	UNIQUE (word),\
	INDEX word_index (word) USING HASH);")

	userConn.query("CREATE TABLE InvertedIndex (\
	word_id	int NOT NULL,\
	document_id int NOT NULL,\
	term_frequency int NOT NULL DEFAULT 0 COMMENT 'the number of appearances this word (word_id) makes in the document (document_id)',\
	in_title TINYINT(1) DEFAULT 0,\
	PRIMARY KEY (word_id, document_id),\
	INDEX doc_index (document_id),\
	FOREIGN KEY (word_id) REFERENCES KeyWords(word_id) ON DELETE CASCADE,\
	FOREIGN KEY (document_id) REFERENCES Documents(document_id) ON DELETE CASCADE);")

	userConn.query("CREATE TABLE IndexPositions (\
	word_id	int NOT NULL,\
	document_id int NOT NULL,\
	position int NOT NULL COMMENT 'the word position of this this word (word_id) in the document (document_id)',\
	PRIMARY KEY (word_id, document_id, position),\
	FOREIGN KEY (word_id, document_id) REFERENCES InvertedIndex(word_id, document_id) ON DELETE CASCADE,\
	FOREIGN KEY (document_id) REFERENCES Documents (document_id) ON DELETE CASCADE);")

	userConn.close()

if __name__ == '__main__':
    main()
