# -*- coding: utf-8 -*-
import json
import urllib
import urllib2
import unicodecsv as csv

with open("list.csv", "r") as csvinput:
    with open("completeList.csv", "w") as csvoutput:
        writer = csv.writer(csvoutput, delimiter=";", quotechar="|", quoting=csv.QUOTE_MINIMAL, encoding='utf-8')
        reader = csv.reader(csvinput, delimiter=";")
        for row in reader:
            print "Getting infos for " + row[0]
            string = urllib.urlencode({'t': row[0].encode('utf-8')})
            result = json.load(urllib2.urlopen("http://www.omdbapi.com/?{title}&y={year}&plot=short&r=json".format(title=string, year=row[1])))
            if (result["Response"] == "True"):
                writer.writerow([result['Title'], result['Year'], result['Genre'].encode('utf-8').split(', '), result['Director'].encode('utf-8').split(', '), result['Actors'].encode('utf-8').split(', '), result['Country'].encode('utf-8').split(', '), result['imdbRating']])

