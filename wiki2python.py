#extract wikipedia table on the page http://en.wikipedia.org/wiki/List_of_districts_of_Germany
#based on tutorial in https://adesquared.wordpress.com/2013/06/16/using-python-beautifulsoup-to-scrape-a-wikipedia-table/
from BeautifulSoup import *
import urllib2


def GetTable():
	wiki   = "http://en.wikipedia.org/wiki/List_of_districts_of_Germany"
	header = {'User-Agent': 'Mozilla/5.0'} #Needed to prevent 403 error on Wikipedia
	req    = urllib2.Request(wiki,headers=header)
	page   = urllib2.urlopen(req)
	soup   = BeautifulSoup(page)
 
	table = soup.find("table", { "class" : "wikitable sortable" })
	print table


	#columns of the wikitable 
	# District
	# Type 	
	# Land 	
	# Capital 
	T = [];
	for row in table.findAll("tr"):
    	cells = row.findAll("td")
    	#For each "tr", assign each "td" to a variable.
    	if len(cells) == 4:
        	T.append([ cells[0].find(text=True), cells[1].find(text=True), cells[2].find(text=True), cells[3].find(text=True) ]);

	#now we have list but we would like to have the coordinates.
	# We will ask gmap for the coordinates...