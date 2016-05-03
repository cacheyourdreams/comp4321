#!/usr/bin/python
from Queue import Queue
import MySQLdb #mySQL
from scrapy.selector import HtmlXPathSelector
from scrapy.http import HtmlResponse
import urllib2 #http
from urlparse import urljoin #relative to absolute urls
import sys, getopt #read command line args
from db import Database
from indexer import Indexer
import re
from datetime import datetime
import email.utils as eut


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

		self.myIndexer = Indexer()
		self.document_id = 0
		
		urlq = Queue()
		urlq.put(url)
		self.crawl(urlq, limit)

		self.myIndexer.close()

	#index all terms on the web page and return the list of links
	def scrape (self, url):
		print "scraping ", url
		request = urllib2.Request(url)
		#request.add_header('User-Agent', 'HKUSTCrawler/0.1')

		try:
			http_response = urllib2.urlopen(request)
		except urllib2.URLError, e:
			print "Error loading url", url, "\n", e
			return []
		htmlbody = http_response.read()

		scrapy_response = HtmlResponse(url=url, body=htmlbody)
		selector = HtmlXPathSelector(scrapy_response)
		words = selector.select("//head//title/text()|//body//text()[not(ancestor::script)]").re('[A-Za-z0-9][A-Za-z0-9\-_]*')
		titleWords = selector.select("//head//title/text()").re('[A-Za-z0-9][A-Za-z0-9\-_]*')
		print "    words:",
		for i in range(0, min(len(words), 7)):
			print words[i], ",",
		print "..."

		title = ' '.join(selector.select("//head/title/text()").re("[[A-Za-z0-9][A-Za-z0-9\-_]*"))
		
		#try and get modified date
		modified = None
		#try and read the last-modified http header (although most pages do not specify this)
		strLastMod = ""
		strDate = ""
		for i in http_response.info():
			if (str(i) == "last-modified"):
				strLastMod = http_response.info()[i]
			elif (str(i) == "date"):
				strDate = http_response.info()[i]
		if (strLastMod != ""):
			modified = datetime(*eut.parsedate(strLastMod)[:6])
		
		#try and get modified date from html body
		date = selector.select("//p[contains(@class, \"right\")]/text()").re('(?<=Last updated on )\d{4}\-\d{2}\-\d{2}')
		
		if (len(date) > 0):
			modified = datetime.strptime(date[0], "%Y-%m-%d")
		
		#if no last-modified header was provided, then just use the date header
		if (modified == None && strDate != ""):
			modified = datetime(*eut.parsedate(strLastMod)[:6])
		
			
		self.document_id = self.myIndexer.indexDocument(url, title, len(words), modified)
		print "id: ", self.document_id
		
		print "indexing words..."
		print self.myIndexer.indexWords(self.document_id, words, titleWords), " words indexed successfully "

		links = selector.select("//a/@href").extract()
		linklist = [urljoin(url, l) for l in links]
		
		self.myIndexer.indexLinks(self.document_id, linklist)
		
		try: #remove self links
			linklist.remove(url)
		except ValueError, ve:
			pass
		
		return linklist

	def crawl (self, urlq, limit):
		while (self.document_id < limit and urlq != None):
			#limit = limit - 1
			#try:
			map(urlq.put, self.scrape(urlq.get()))
			#except Exception, e:
			#	print "fatal error while crawling"
			#	print e
		return 0

if __name__ == '__main__':
    Spider().main(sys.argv[1:])
