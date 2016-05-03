#!/usr/bin/python
print('Content-type: text/html\r\n\r')

import cgi, json
import cgitb; cgitb.enable()
import datetime
from searcher import Searcher

cgitb.enable()  # for troubleshooting

#the cgi library gets vars from html
data = cgi.FieldStorage()
mySearcher = Searcher()
html = ""

query = data.getvalue('query')
a = datetime.datetime.now()
results = mySearcher.getSearchResults(query)
b = datetime.datetime.now()
c = b - a
n = 0

# r[1][0] = rank
# r[1][1] = url
# r[1][2] = modified
# r[1][3] = size
# r[1][4] = dict{keyword: freq}
# r[1][5] = array{parents}
# r[1][6] = array{children}

# set up data structure to hold json skeleton
data = {}
# set of result objects
res = []

# handle no results found case
if len(results) <1 :
	data['error'] = "No results found for: " + query;
	json_data = json.dumps(data)
	res.append(json_data);
	print json.dumps([dict(result=r) for r in res])
else:
	# stats json
	data['time_taken'] = str(c.total_seconds()) + " seconds.";
	data['total_results'] = str(len(results)) + " (50 shown)" if len(results) > 50 else str(len(results));
	json_data = json.dumps(data)
	res.append(json_data);

	# variable to limit output
	i = 0;

	for r in results:

		# limit output 50 results
		if (i > 49):
			break;
		i+=1;

		# unpack result
		url = r[0]
		rank = r[1][0]
		title = r[1][1]
		modified = r[1][2]
		size = r[1][3]
		keywords = r[1][4]
		parents = r[1][5]
		children = r[1][6]

		# create dictionary
		data['url'] = url;
		data['rank'] = rank;
		data['title'] = title;
		data['modified'] = modified;
		data['size'] = size;
		data['keywords'] = keywords;
		data['parents'] = parents;
		data['children'] = children;
		json_data = json.dumps(data)
		res.append(json_data);

	# output string containing array of json
	print json.dumps([dict(result=r) for r in res])
