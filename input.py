import csv

with open("list.csv", "r") as csvinput:
    reader = csvinput.reader()
    for row in reader:
    #If the row does not contain a value for the rating of this movie
        var = raw_input("Rate this movie " + row[0])
        #if input is empty, I did not see the movie, do not do anything
        #if input is a valid 0 to 10 numbers, write it into an other csv
