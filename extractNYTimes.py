#-*- coding: utf-8 -*-
import re
import urllib
from lxml import html
from bs4 import BeautifulSoup

url = "http://www.nytimes.com/ref/movies/1000best.html"

html =  urllib.urlopen(url).read()

soup = BeautifulSoup(html, 'html.parser')
bestMovies =  soup.find(id='bestMovies')
tables = bestMovies.find_all("table")
name = tables[0].find('a').string
regex = ur"(.*?)\(\d*?\)"

for table in tables:
    for row in table.find_all('tr')[1:]:
        string = row.find('a').string.encode('utf-8')
        matches = re.finditer(regex, string)
        for matchNum, match in enumerate(matches): 
            print match.group(1).strip()
