#-*- coding: utf-8 -*-
from __future__ import print_function
import re
import urllib
from bs4 import BeautifulSoup

f = open('list.csv','w')
#Extract the movies which are not older than 20
for year in range(1996,2017):
    #Obtain the HTML and parse using Beautiful soup
    print("Obtaining the list for the year {year}".format(year = year))
    url = "https://www.rottentomatoes.com/top/bestofrt/?year={year}".format(year = year)
    html =  urllib.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')

    #Magic happens: we need to know what does the HTML looks like first, but we can then extract everything
    rows = soup.find_all('a', {'unstyled', 'articlelink'},itemprop='url')
    #This regex allows to extract the name and the year of the movie
    regex = ur"(.*?)\s\((\d*)\)"
    for row in rows:
        matches = re.finditer(regex, row.string)
        for matchNum, match in enumerate(matches):
            #We print it as a csv format, first column: name, second column: year
            f.write('{name};{year}\n'.format(name = match.group(1).encode('utf-8'), year = match.group(2)))
    print('Done !')
#Comment ce flim a-t-il pu être oublié ??
f.write('La classe américaine;1999')
f.close()
