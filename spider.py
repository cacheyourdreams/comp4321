#!/usr/bin/python
import MySQLdb #mySQL
import urllib2 #http
import sys, getopt #read command line args
import db
import indexer

class Spider:
	def main(self, argv):
		#get command line arguments
		try:
			opts, args = getopt.getopt(argv, "s:n:", [])
		except getopt.GetoptError as err:
			print err
			print "Usage: spider.py -s \"starting url\" -n \"number of pages to retrieve\""
			sys.exit(2)
		
		url = "";
		limit = -1
		for opt, arg in opts:
			if opt == '-s':
				url = arg
			elif opt == '-n':
				try:
					limit = int(arg)
				except ValueError:
					print "-n option requires an integer number"
					sys.exit(2)
		if (url == "" or limit == -1):
			print "Usage: spider.py -s \"starting url\" -n \"number of pages to retrieve\""
			sys.exit(2)
			
		print "hello world, ", url, ", ", limit

if __name__ == '__main__':
    Spider().main(sys.argv[1:])







