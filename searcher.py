#!/usr/bin/python
import MySQLdb #mySQL
from db import *
from indexer import Indexer
import sys, getopt #read command line args
import re
from math import *
import operator

class Searcher:
	def __init__(self):
		self.myIndexer = Indexer()
		self.dbInstance = Database()

	def main(self, argv):
		#get command line arguments
		try:
			opts, args = getopt.getopt(argv, "s:", [])
		except getopt.GetoptError as err:
			print err
			print "Usage: searcher.py -s \"search query\""
			sys.exit(2)
		query = ""
		for opt, arg in opts:
			if opt == '-s':
				query = arg
		if (query == ""):
			print "Usage: searcher.py -s \"search quey\""
			sys.exit(2)
			
		sortedDocs = self.getSearchResults(query)
		for d in sortedDocs:
			print d
	
	def getSearchResults (self, query):
		searchTerms = self.parseQuery(query)	
		if len(searchTerms) == 0:
			return {}
		queryWordIds = self.getWordIds(searchTerms)
		documentVectors = self.getDocumentVectors(searchTerms)
		sortedDocs = self.sortDocumentVectors(queryWordIds,documentVectors)
		return sortedDocs
			
	def sortDocumentVectors (self, queryWordIds, documentVectors):
		documents = dict()
		for doc in documentVectors.keys():
			sim = self.cosSim(queryWordIds,documentVectors[doc][1],documentVectors[doc][0])
			#document_size, vector, title, modified, keyword:freq, parents, children
			#r[0] = url
			#r[1][0] = rank
			#r[1][1] = title
			#r[1][2] = modified
			#r[1][3] = size
			#r[1][4] = dict{keyword: freq}
			#r[1][5] = array{parents}
			#r[1][6] = array{children}

			documents[doc] = [sim, documentVectors[doc][2], documentVectors[doc][3], documentVectors[doc][0], documentVectors[doc][4], documentVectors[doc][5], documentVectors[doc][6]]
		return sorted(documents.items(), key=operator.itemgetter(1))
		
	
	def getDocumentVectors(self, terms):
		N = 0
		self.dbInstance.query("SELECT COUNT(*) FROM Documents;")
		N = self.dbInstance.fetchOne()[0]
		
		#get inverted index entries for each word in the search term
		sql_select = "SELECT InvertedIndex.word_id, InvertedIndex.document_id, InvertedIndex.term_frequency, document_url, document_frequency, document_size, max_tf, document_title, InvertedIndex.in_title, modified, fetched, word FROM InvertedIndex LEFT JOIN KeyWords on InvertedIndex.word_id=KeyWords.word_id LEFT JOIN Documents ON Documents.document_id = InvertedIndex.document_id  WHERE InvertedIndex.word_id IN (SELECT word_id FROM KeyWords WHERE word=%s"
		for x in range(1,len(terms)):
			sql_select = sql_select + " OR word = %s"
		sql_select = sql_select + ");"
		
		self.dbInstance.query(sql_select, terms)
		rows = self.dbInstance.fetchAll()
		
		documentVectors = dict()
		indexValue = 3
		
		for row in rows:
			docVector = dict()
			#do we already have at least one entry for this document in our sparse matrix?
			if row[indexValue] in documentVectors:
				docVector = documentVectors[row[indexValue]][1]
			else:
				#if not, create a new entry
				#get links to/from
				sql_select_links = "SELECT document_url, child_url FROM Links LEFT JOIN Documents on Documents.document_id = Links.parent_id WHERE Links.parent_id = %s OR Links.child_url = %s;"
				self.dbInstance.query(sql_select_links, (row[1],row[3]))
				links = self.dbInstance.fetchAll()
				parents = []
				children = []
				for link in links:
					if link[1] == row[3]:
						parents.append(link[0])
					else:
						children.append(link[1])
				#document_size, vector, title, modified, keyword:freq, parents, children
				documentVectors[row[indexValue]] = [row[5], dict(), row[7], row[9], dict() , parents, children]
			#obtain normalised tf*idf value
			val = (float(row[2])*log(N/float(row[4]),2)) / float(row[6])
			#give a boost to the weight if it appears in the document title
			val = val * (1.5 if row[8] == 1 else 1) 
			docVector[row[0]] = val
			documentVectors[row[indexValue]][1] = docVector
			documentVectors[row[indexValue]][4][row[11]] = row[2]
		
		return documentVectors
	
	def getWordIds(self, words):
		wordIds = []
		#sanity check
		if len(words) == 0:
			return wordIds
		
		#select the word ids cooresponding to the given words form the database
		sql_select = "SELECT word_id FROM KeyWords WHERE word=%s"
		for x in range(1,len(words)):
			sql_select = sql_select + " OR word = %s"
		sql_select = sql_select + ";"
		self.dbInstance.query(sql_select, words)
		rows = self.dbInstance.fetchAll()
		for row in rows:
			wordIds.append(row[0])
		return wordIds
		
	def parseQuery(self, query):
		#select only alphanumeric words (allow dashes and underscores as well)
		queryTerms = re.split("[^A-Za-z0-9\-_]+", query)
		searchTerms = []
		
		#get the indexer to do stemming and stop word removal for us
		for w in queryTerms:
			if (self.myIndexer.isStopword(w)):
				continue
			stemmed = self.myIndexer.getStemmed(w)
			searchTerms.append(stemmed)
		return searchTerms

	
	def cosSim (self, queryTerms, docVector, docLength):
		#just treat each term as weight 1, so all terms in query are equally important
		dotProduct = 0
		for qt in queryTerms:
			if qt in docVector:
				dotProduct = dotProduct + docVector[qt]
		return dotProduct / (docLength * len(queryTerms))
		
		
if __name__ == '__main__':
    Searcher().main(sys.argv[1:])
