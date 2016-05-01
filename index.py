#!/usr/bin/python
import cgi
import cgitb; cgitb.enable()
from searcher import Searcher

print "Content-type: text/html"
print


mySearcher = Searcher()
form = cgi.FieldStorage()
html = ""


if "query" in form:
	query = form.getvalue('query')
	results = mySearcher.getSearchResults(query)
	for r in results:
		html = "<li><a href=\""+r[0]+"\">"+r[1][1]+"</a></li>" + html

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
</body>
</html>""" % html
