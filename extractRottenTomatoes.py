#-*- coding: utf-8 -*-
import re
import urllib
from bs4 import BeautifulSoup

for year in range(1996,2016):
    url = "https://www.rottentomatoes.com/top/bestofrt/?year={year}".format(year = year)
    
    html =  urllib.urlopen(url).read()
    
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find_all('a', {'unstyled', 'articlelink'},itemprop='url')
    regex = ur"(.*?)\s\((\d*)\)"
    for row in rows:
        matches = re.finditer(regex, row.string)
        for matchNum, match in enumerate(matches):
            print('{name};{year}'.format(name = match.group(1).encode('utf-8'), year = match.group(2)))
