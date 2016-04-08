# comp4321

##Installation

###Dependencies

The following packages are required for correct operation of the code:
* python 2.7
* python-mysql
* scrapy
* stemming 1.0 (included in project)
* mysql (running on local host)

##Set up
The code includes a setup.py script which will biuld all the database tables. This will create a new database and mysql user. The commands can also be run in mysql directly:

```SQL
DROP DATABASE IF EXISTS comp4321;
GRANT USAGE ON *.* TO 'user4321'@'localhost';"
DROP USER 'user4321'@'localhost';"
CREATE DATABASE comp4321;
GRANT ALL PRIVILEGES ON comp4321.* To 'user4321'@'localhost' IDENTIFIED BY 'gryphon';

CREATE TABLE Documents (
	document_id int NOT NULL AUTO_INCREMENT,
	document_url varchar(255) NOT NULL,
	document_title varchar(255) NOT NULL,
	document_size int NOT NULL,
	modified DATETIME,
	fetched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (document_id),
	UNIQUE (document_url),
	INDEX url_index (document_url));
	
CREATE TABLE Links (
  parent_id int NOT NULL,
  child_url varchar(255) NOT NULL,
  PRIMARY KEY (parent_id, child_url),
  FOREIGN KEY (parent_id) REFERENCES Documents(document_id) ON DELETE CASCADE);
  
CREATE TABLE KeyWords (
	word_id	int NOT NULL AUTO_INCREMENT,
	word VARCHAR(255) NOT NULL,
	document_frequency int NOT NULL COMMENT 'the number of unique documents which contain at least one instance of the word',
	PRIMARY KEY (word_id),
	UNIQUE (word),
	INDEX word_index (word) USING HASH);
	
CREATE TABLE InvertedIndex (
	word_id	int NOT NULL,
	document_id int NOT NULL,
	term_frequency int NOT NULL DEFAULT 0 COMMENT 'the number of appearances this word (word_id) makes in the document (document_id)',
	PRIMARY KEY (word_id, document_id),
	INDEX doc_index (document_id),
	FOREIGN KEY (word_id) REFERENCES KeyWords(word_id) ON DELETE CASCADE,
	FOREIGN KEY (document_id) REFERENCES Documents(document_id) ON DELETE CASCADE);
	
CREATE TABLE IndexPositions (
	word_id	int NOT NULL,
	document_id int NOT NULL,
	position int NOT NULL COMMENT 'the word position of this this word (word_id) in the document (document_id)',
	PRIMARY KEY (word_id, document_id, position),
	FOREIGN KEY (word_id, document_id) REFERENCES InvertedIndex(word_id, document_id) ON DELETE CASCADE,
	FOREIGN KEY (document_id) REFERENCES Documents (document_id) ON DELETE CASCADE);
```

##Phase 1
In order to simply demonstrate the phase 1 requirements, once the above setup is complete, we first run the spider over 30 pages, starting at http://www.cse.ust.hk:

```Bash
python spider.py -s "http://www.cse.ust.hk/" -n 30
```

This will make appropriate use of the Indexer class contained in indexer.py, to create the index entries in the MySQL database. Once this program completes, in order to extract the entries in the specified format, i.e.:

```
Page title
URL
Last modification date, size of page
Keyword1 freq1; Keyword2 freq2; Keyword3 freq3; …...
Child Link1
Child Link2 .....
```

We simply run the phase1_test_program.py script, i.e.

```Bash
python phase1_test_program.py
```

This will print all the entries in the database to the STDOUT. In order to save this in the spider_result.txt file, we use simple redirection on the command line, i.e.:

```Bash
python phase1_test_program.py > spider_result.txt
```

##Code structure
The project is split up into seperate files in order to improve code readability and maintenance. OOP priniciples have been used in the design, for example, a database wrapper class, defined in db.py, means that the details of the database backend is hidden from the rest of the code, meaning that we could easily swap out the mysql engine at a later date, if a different database provider was to be used instead.

###db.py
This file contains a single class, "Database", which serves as a wrapper for the MySQLdb connection. Any interactions with the database backend, such as updating the index records or retrieving results, should be routed through this class. This script should never be run directly, and should only be used as a module in the other scripts.

###spider.py
This class is runable, unlike db.py and indexer.py. But it does makes use of both of the aforementioned scripts as modules. The spider takes two arguments when being run:

* -s: the url of the starting page, e.g. -s "http://www.cse.ust.hk"
* -n: the number of links to follow in total, e.g. -n 30

The spider will follow links using a breadth-first strategy, as specified in the assignment. This behaviour can be implemented using a Queue, as placing new entries at the back ensures that any items at a higher level in the tree will be processed first (as they will already have been added to the Queue). While this does not maintain a tree structure, it is a straightforward way of achieving the desired output.

This file also handles the parsing of the html from the webpages. This is handled using the scrapy library, combined with some RegEx:

```python
words = selector.select("//head//title/text()|//body//text()[not(ancestor::script)]").re('[[A-Za-z0-9][A-Za-z0-9\-_]*')
```

This selects all alphanumeric words, which must start with a letter or number but may additionally contain underscores and dashes (this is according the the regular experssion filter included at the end of the line). The words must also appear within the \<body\> html tag, and not within a \<script\> tag.

###indexer.py

The class formats the data scraped from the webpages by spider.py into the correct shape for the database backend. If a record already exists for any of the entries (e.g. a common keyword is likely to have been seen before) then the index.py will extract the ID of the existing record, otherwise it will insert a new record and return the new ID, using the lastrowid property.

The indexer also applies stop word removal, using the provided stopwords.txt file, and stemming, using a standard implementation of Porter's algorithm, using a public python library [https://pypi.python.org/pypi/stemming/1.0]. 

##Database structure

