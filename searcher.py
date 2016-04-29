import MySQLdb #mySQL
from db import *
import sys, getopt #read command line args


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
s
		print query
if __name__ == '__main__':
    Searcher().main(sys.argv[1:])
