#!/usr/bin/python
import cgi
import cgitb; cgitb.enable()
import datetime
from searcher import Searcher

print "Content-type: text/html"
print


mySearcher = Searcher()
form = cgi.FieldStorage()
html = ""


if "query" in form:
	query = form.getvalue('query')
	a = datetime.datetime.now()
	results = mySearcher.getSearchResults(query)
	b = datetime.datetime.now()
	c = b - a
	n = 0
	for r in results:
		n = n + 1
		if n == 51:
			break
		html = "<li><a href=\""+r[0]+"\">"+cgi.escape(r[1][1])+"</a></li>" + html

print """
<html>
<head>
<title>
COMP4321
</title>
</head>
<body>
<form action='index.py' method='get'>
<label>Search:</label>
<input type='text' name='query' value='' placeholder="Enter Search Query Here"/>
</form>
<h1>Results</h1>
<ul>
%s
</ul>
<p>%s results found in %f seconds</p>
</body>
</html>""" % (html, ("50+" if n == 51 else str(n)), c.total_seconds())
