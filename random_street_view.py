#Example usage: python random_street_view.py DEU
# it will generate a random coordinate based on the country mask, will then transform this coordinate
# to human readable address (e.g. street, number etc.) by asking google, and finally will capture a street
# view from that point. It is possible that that there is no street view at that location, in that case, it will 
# reiterate until success.

import argparse
import os
import random
import shapefile  # http://code.google.com/p/pyshp/
import sys
import urllib
import json

# Optional, http://stackoverflow.com/a/1557906/724176
try:
	import timing
except:
	pass

# Google Street View Image API
# 25,000 image requests per 24 hours
# See https://developers.google.com/maps/documentation/streetview/
API_KEY = open('/Users/copter/Documents/googleapi/apikey.txt','r').read()
GOOGLE_URL = "http://maps.googleapis.com/maps/api/streetview?sensor=false&size=640x640&fov=120&key=" + API_KEY
# LL will be replaced by the candidate coordinate (LL will be replaced accordingly)
GOOGLE_DIR = "http://maps.googleapis.com/maps/api/directions/json?origin=LL&destination=LL"


IMG_PREFIX = "img_"
IMG_SUFFIX = ".jpg"

parser = argparse.ArgumentParser(description="Get random Street View images from a given country")
parser.add_argument('country',  help='ISO 3166-1 Alpha-3 Country Code')
args = parser.parse_args()


# Determine if a point is inside a given polygon or not
# Polygon is a list of (x,y) pairs.
# http://www.ariel.com.au/a/python-point-int-poly.html
def point_inside_polygon(x, y, poly):
	n = len(poly)
	inside = False
	p1x, p1y = poly[0]
	for i in range(n+1):
		p2x, p2y = poly[i % n]
		if y > min(p1y, p2y):
			if y <= max(p1y, p2y):
				if x <= max(p1x, p2x):
					if p1y != p2y:
						xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
					if p1x == p2x or x <= xinters:
						inside = not inside
		p1x, p1y = p2x, p2y
	return inside

print "Loading borders"
shape_file = "/Users/copter/Documents/WorldMasks/TM_WORLD_BORDERS-0/TM_WORLD_BORDERS-0.3.shp"
if not os.path.exists(shape_file):
	print "Cannot find " + shape_file + ". Please download it from "
	"http://thematicmapping.org/downloads/world_borders.php and try again."
	sys.exit()

sf = shapefile.Reader(shape_file)
shapes = sf.shapes()

#TODO:
#here find the coordinates of the city of interest 


print "Finding country"
for i, record in enumerate(sf.records()):
	if record[2] == args.country.upper():
		print record[2], record[4]
		print shapes[i].bbox
		min_lon = shapes[i].bbox[0]
		min_lat = shapes[i].bbox[1]
		max_lon = shapes[i].bbox[2]
		max_lat = shapes[i].bbox[3]
		borders = shapes[i].points
		break

print "Getting images"
attempts, country_hits, imagery_hits, imagery_misses = 0, 0, 0, 0
MAX_URLS = 25000
IMAGES_WANTED = 1

if not os.path.exists(args.country):
	os.makedirs(args.country)

try:
	while(True):
		attempts += 1
		#TODO:
		#Here, get a random coordinate from a circle of a given diameter around the center.


		rand_lat = random.uniform(min_lat, max_lat)
		rand_lon = random.uniform(min_lon, max_lon)
		# print attempts, rand_lat, rand_lon
		# Is (lat,lon) inside borders?
		if point_inside_polygon(rand_lon, rand_lat, borders):
			print "  In country"
			country_hits += 1
			lat_lon = str(rand_lat) + "," + str(rand_lon)
			outfile = os.path.join(args.country, IMG_PREFIX + lat_lon + IMG_SUFFIX)
			url     = GOOGLE_DIR.replace("LL",lat_lon) 
			try:
				source     = urllib.urlopen(url)
				jcode      = json.load(source)
				address    = jcode["routes"][0]["legs"][0]["start_address"]
				#now create the correct URL with the valid address
				url_valid  = GOOGLE_URL + "&location=" + address
				urllib.urlretrieve(url_valid,outfile)
			except:
				pass
			if os.path.isfile(outfile):
				# Check size and delete "Sorry, we have no imagery here".
				# Note: hardcoded based on current size of default.
				# Might change.
				# Will definitely change if you change requested image size.
				if os.path.getsize(outfile) < 10000:  # bytes
					print "    No imagery"
					imagery_misses += 1
					os.remove(outfile)
				else:
					print "    ========== Got one! =========="
					imagery_hits += 1
					if imagery_hits == IMAGES_WANTED:
						break
			if country_hits == MAX_URLS:
				break
except KeyboardInterrupt:
	print "Keyboard interrupt"

print "Attempts:\t", attempts
print "Country hits:\t", country_hits
print "Imagery misses:\t", imagery_misses
print "Imagery hits:\t", imagery_hits

# End of file
