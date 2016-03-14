#!/usr/bin/python
import MySQLdb #mySQL
from scrapy.selector import HtmlXPathSelector
from scrapy.http import HtmlResponse
import urllib2 #http
import sys, getopt #read command line args
from db import Database
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
		
		#open database or die
		try:
			self.dbConn = Database()
		except Exception, e:
			print "Database connection could not be started, have you run setup.py?"
			print e
			sys.exit(1)
		
		self.crawl(url, limit)

	#index all terms on the web page and return the list of links
	def scrape (self, url):
		http_response = urllib2.urlopen(url)
		htmlbody = http_response.read()
		
		scrapy_response = HtmlResponse(url=url, body=htmlbody)		
		selector = HtmlXPathSelector(scrapy_response)
		
		print ''.join(selector.select("//body//text()").extract()).strip()
		return 0
		
	def crawl (self, url, limit):
		self.scrape(url)
		return 0
	
	

if __name__ == '__main__':
    Spider().main(sys.argv[1:])







