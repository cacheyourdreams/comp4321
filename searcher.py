import MySQLdb #mySQL
from db import *
from indexer import Indexer
import sys, getopt #read command line args
import re
from math import *
import operator

class Searcher:
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
		
		myIndexer = Indexer()
		self.dbInstance = Database()
		
		N = 0
		
		self.dbInstance.query("SELECT COUNT(*) FROM Documents;")
		N = self.dbInstance.fetchOne()[0]
		
		queryTerms = re.split("[^A-Za-z0-9\-_]+", query)
		
		searchTerms = []
		
		for w in queryTerms:
			if (myIndexer.isStopword(w)):
				continue
			stemmed = myIndexer.getStemmed(w)
			searchTerms.append(stemmed)
			
		if len(searchTerms) == 0:
			print "Please provide at least one non stop word!"
			sys.exit(2)
			
		queryWordIds = []
		sql_select = "SELECT word_id FROM KeyWords WHERE word=%s"
		for x in range(1,len(searchTerms)):
			sql_select = sql_select + " OR word = %s"
		sql_select = sql_select + ";"
		self.dbInstance.query(sql_select, searchTerms)
		rows = self.dbInstance.fetchAll()
		for row in rows:
			queryWordIds.append(row[0])
		
		sql_select = "SELECT InvertedIndex.*, document_url, document_frequency, document_size FROM InvertedIndex LEFT JOIN KeyWords on InvertedIndex.word_id=KeyWords.word_id LEFT JOIN Documents ON Documents.document_id = InvertedIndex.document_id  WHERE InvertedIndex.word_id IN (SELECT word_id FROM KeyWords WHERE word=%s"
		for x in range(1,len(searchTerms)):
			sql_select = sql_select + " OR word = %s"
		sql_select = sql_select + ");"
		
		self.dbInstance.query(sql_select, searchTerms)
		rows = self.dbInstance.fetchAll()
		
		documents = dict()
		
		documentVectors = dict()
		indexValue = 3
		
		for row in rows:
			docVector = dict()
			if row[indexValue] in documentVectors:
				docVector = documentVectors[row[indexValue]][1]
			else:
				documentVectors[row[indexValue]] = [row[5], dict()]
			val = (float(row[2])*log(N/float(row[4]),2)) / float(row[5]) #normalise by document size for now, should be max(tf) eventually
			docVector[row[0]] = val
			documentVectors[row[indexValue]][1] = docVector
		
		for doc in documentVectors.keys():
			documents[doc] = self.cosSim(queryWordIds,documentVectors[doc][1],documentVectors[doc][0])
		
		
		sortedDocs = sorted(documents.items(), key=operator.itemgetter(1))
		
		for d in sortedDocs:
			print d
		
	def cosSim (self, queryTerms, docVector, docLength):
		#just treat each term as weight 1, so all terms in query re equally important
		dotProduct = 0
		for qt in queryTerms:
			if qt in docVector:
				dotProduct = dotProduct + docVector[qt]
		return dotProduct / (docLength * len(queryTerms))
		
		
if __name__ == '__main__':
    Searcher().main(sys.argv[1:])
