import urllib

gtfs_url = "http://www.mbta.com/uploadedfiles/MBTA_GTFS.zip"

feed_info = "http://www.mbta.com/uploadedfiles/feed_info.txt"

params = urllib.urlencode({'spam': 1, 'eggs': 2, 'bacon': 0})
f = urllib.urlopen("http://www.mbta.com/uploadedfiles/feed_info.txt")
print f.read()

