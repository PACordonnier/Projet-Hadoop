# Introduction
Le sujet de cette étude est simple : Comment le Big Data peut il m'aider à choisir un film à regarder ce soir ?

En effet, j'ai une grosse vidéothèque de film à la demande chez moi, sauf que je passe souvent autant de temps à me demander quoi voir plutôt que de regarder le film. Je suis sur qu'en fonction des films que j'aime, on pourrait me proposer d'autres films que je devrais apprécier.

Je n'invente rien avec ce projet, les recommandations YouTube ou Netflix le font déjà et le but est davantage de chercher à le faire en utilisant les outils Big Data.

Pour trouver LE film que j'ai envie de mater ce soir, d'habitude c'est :

* Regarder les dernières sorties sur l'IMDB ou allociné
* Regarder des affiches de films
* Lire des synopsis
* Regarder des notes

Et éventuellement, un truc sortira du lot et je le regarderai, sauf il n'est pas déjà minuit...

Ce projet va se découper en cinq parties :

* Obtenir une liste de noms de films
* Récupérer des informations sur ces films
* Charger ses films sur le cluster 
* Indiquer quels films j'ai déjà regardé
* Faire de la prédiction et me fournir un résultat

Il serait aussi très intelligent de faire marcher ce service auprès d'un grand nombre d'utilisateurs et ainsi profiter de la puissance de la communauté.

# Partie 1 : Une jolie liste de films 

L'idée ici c'est d'obtenir une liste comprenant le plus de films possibles, afin d'alimenter ma "base de données" de films. Le plus simple pour cela c'est de chercher des listes "Les meilleurs films de l'année XXXX/ de tous les temps"

[Top 1000 films du New York Times](http://www.nytimes.com/ref/movies/1000best.html)

[Top 250 IMDB](http://www.imdb.com/chart/top)

[Top RottenTomatoes par année](https://www.rottentomatoes.com/top/bestofrt/?year=2016)

On pourrait avoir une liste presque exhaustive en utilisant wikipedia qui fournit une liste alphabétique très complète mais on va dire que je veux regarder un bon film (ou en tout cas que des gens ont jugé bon)

Ces sites fournissent du magnifique HTML uniquement, pour extraire les données qui m'intéressent on va utiliser un script python avec la librairie [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

Voilà un code qui permet d'extraire les 100 meilleurs films par année des 20 dernières années sur rotten tomatoes:

```python
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
f.write('La classe americaine;1993')
f.close()
```

J'ai donc maintenant un superbe fichier csv de 2000 lignes, la prochaine étape de trouver des informations plus complète sur ces films !

# Partie 2 : Le plein d'infos
Tout d'abord je me suis demandé sur quels critères je me basais pour regarder un film :

* De quel genre de films s'agit-il ? (Action, Sci-fi, Humour etc...)
* Quand est il sorti ?
* Comment a-t-il été noté ? (Sur IMDB, RottenTomatoes ou autre)
* Qui est le réalisateur ?
* Qui est l'acteur principal ?
* De quel pays vient il ?

C'est donc ces données qui vont permettre de catégoriser un film.
Je vais utiliser l'api [OMDB](https://www.omdbapi.com/) afin d'obtenir ces infos.

Cette api est très simple d'utilisation, pour la requête `GET http://www.omdbapi.com/?t=Zootopia&y=2016&plot=short&r=json` on obtient:

```json
{

    "Title": "Zootopia",
    "Year": "2016",
    "Rated": "PG",
    "Released": "04 Mar 2016",
    "Runtime": "108 min",
    "Genre": "Animation, Adventure, Comedy",
    "Director": "Byron Howard, Rich Moore, Jared Bush",
    "Writer": "Byron Howard (story by), Rich Moore (story by), Jared Bush (story by), Jim Reardon (story by), Josie Trinidad (story by), Phil Johnston (story by), Jennifer Lee (story by), Jared Bush (screenplay), Phil Johnston (screenplay)",
    "Actors": "Ginnifer Goodwin, Jason Bateman, Idris Elba, Jenny Slate",
    "Plot": "In a city of anthropomorphic animals, a rookie bunny cop and a cynical con artist fox must work together to uncover a conspiracy.",
    "Language": "English",
    "Country": "USA",
    "Awards": "2 wins & 4 nominations.",
    "Poster": "https://images-na.ssl-images-amazon.com/images/M/MV5BOTMyMjEyNzIzMV5BMl5BanBnXkFtZTgwNzIyNjU0NzE@._V1_SX300.jpg",
    "Metascore": "78",
    "imdbRating": "8.1",
    "imdbVotes": "220,927",
    "imdbID": "tt2948356",
    "Type": "movie",
    "Response": "True"

}
```

En scriptant ceci, on peut générer un fichier .csv qui contient plein d'infos sur tous les films:

```python
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
```

Voila la sortie attendue:

> Titre, Année, Genre(s), Réalisateur(s), Acteurs principaux, Pays, Note IMDB
>
> Black Hawk Down;2001;['Drama', 'History', 'War'];['Ridley Scott'];['Josh Hartnett', 'Ewan McGregor', 'Tom Sizemore', 'Eric Bana'];['USA', 'UK'];7.7

# Partie 3: Insérer les données dans le cluster

On possède maintenant un fichier .csv contenant pas mal de lignes, on peut déjà le traiter de cette manière avec un simple MapReduce.

```java
protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
            String line = value.toString();
            String[] lineSplit = line.split(";");
            String[] originSplit = lineSplit[3].split(",");
            for (String s : originSplit) {
                if (s.equals("")) {
                    s = "?";
                }
                String replace = s.trim().replace("]", "").replace("[", "");
                word.set(replace.substring(1,replace.length()-1));
                context.write(word, one);
            }
        }

protected void reduce(Text key, Iterable<IntWritable> values, Context context) throws IOException, InterruptedException {
            int sum = 0;
            for (IntWritable value : values) {
                sum += value.get();
            }
            context.write(key, new IntWritable(sum));
        }
```

On obtient ainsi les réalisateurs présents dans le fichier avec le nombre de films présents dans cette liste, le gagnant est Steven Spielberg !
Pour ce qui est des pays d'origines, le gagnant est sans suprises les Etats-Unis avec presque 1200 films sur une liste de 1400.

Pour des raisons plus pratiques, on peut aussi insérer ces données dans une base de données HBase ou HiveSQL.
Je pense que le plus judicieux serait HBase. On va en effet très peu chercher à modifer cette base, mais on doit néanmoins lui ajouter des données (Un booléen pour savoir si j'ai vu le film et une note sur ce film). Je n'ai néanmoins pas eu le temps d'ajouter dans HBase ces données.

Il semble assez commun de remplir HBase depuis un fichier CSV, comme décrit [ici](http://stackoverflow.com/questions/13906847/loading-csv-data-into-hbase#13935434)

# Partie 4: Noter moi-même ces films

Afin d'obtenir une "tendance", il est nécessaire (mais très pénible) de noter moi-même ces films. En effet un algorithme de prédiction va être nécessaire, mais il lui faut pour cela une entrée. Si je lui dis que j'ai adoré tous les films d'action de 2016, il sere enclin à me proposer d'autres films d'actions...

Certains cinéphiles notent depuis de nombreuses années les films qu'ils regardent sur allociné ou imdb. Si c'était le cas, il est possible de récupérer cette liste et d'en alimenter mes données. Ce n'est malheuresement pas mon cas...
Je ne vois pas de solutions miracles autrement que de parcourir la liste des films, par exemple avec un REPL, et de lui attribuer une note rapidement. En python cela ressemblerait à ceci:

```python
with open("list.csv", "r") as csvinput:
    reader = csvinput.reader()
    for row in reader:
    #If the row does not contain a value for the rating of this movie
        var = raw_input("Rate this movie " + row[0])
        #if input is empty, I did not see the movie, do not do anything
        #if input is a valid 0 to 10 number, write it into an other csv
```

Cette étape est forcément fastidieuse, il serait aussi possible de le faire sous forme d'interface graphique web par exemple.

# Partie 5 : Prédiction

Deux types de prédiction sont possibles:

* Seul mon avis compte
* L'avis de la communauté est pris en compte

## Je suis seul !

Dans ce cas, il est nécessaire de "deviner" quels sont les critères qui m'ont fait aimé un film, et de les pondérer à leur juste valeur.

Si on travaille sur la liste des films ayant une bonne note (disons 7/10)

* De quel genre s'agit-il ? Un film possède en général plusieurs genres, se recoupent-ils entre eux ? (Action-SciFi / Drame-SciFi −> Cet homme aime les films de Science-Fiction !)
* Qui est mon réalisateur favori ?
* Qui est mon acteur favori ?
* Plutôt des films récents ou anciens ?
* Quel film que je n'ai pas vu regroupe le plus de ses critères ?

Une proposition peut ensuite être déduite de ses critères. Il est de plus possible de travailler sur les films que je n'ai PAS aimé, afin d'éviter de proposer les films d'un réalisateur que je ne supporte pas.

## Vive la communauté !

La puissance de la déduction peut sûrement se faire à l'aide d'une communauté d'utilisateurs cinéphiles. Le plus simple serait en effet de "catégoriser" les utilisateurs entre eux, afin de créer des groupes. Des algorithmes comme k-means sont déjà prévus pour cette utilisation. (Ces algorithmes sont déjà en grandes parties implémentées dans Spark par exemple)

# Conclusion

J'aurais tellement aimé faire plus pour ce projet. Je n'ai pas correctement su géré mon temps avec les deadlines de fin d'année. Je pense réellement qu'il est faisable "pas trop difficillement" d'obtenir des tendances dans mes goûts cinématographiques. Google et Netflix le font déjà, pourquoi pas moi ?

Plus sérieusement, j'ai surtout travaillé sur la partie ETL/Code du projet, qui m'est le plus familère. La partie purement Big Data est faible. J'ai encore du mal à me représenter les possibilités offertes par Hadoop. Ce projet consiste en effet en un simple ETL suivi d'un peu de Data Science, alors que les technologies sont très nombreuses et m'aurait permis de faire bien mieux ce que j'ai réalisé ici.
