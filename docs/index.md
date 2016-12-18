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
f.write('La classe américaine;1999')
f.close()
```

J'ai donc maintenant un superbe fichier csv de 2000 lignes, la prochaine étape de trouver des informations plus complète sur ces films !

# Partie 2 : Le pleins d'infos
Tout d'abord je me suis demandé sur quels critères je me basais pour regarder un film :

* De quel genre de films s'agit-il ? (Action, Sci-fi, Humour etc...)
* Quand est il sorti ?
* Comment a-t-il été noté ? (Sur IMDB, RottenTomatoes ou autre)
* Qui est le réalisateur ?
* Qui est l'acteur principal ?
* De quel pays vient il ?

C'est donc ces données qui vont permettre de catégoriser un film.
Je vais utiliser l'api [OMDB](https://www.omdbapi.com/) afin d'obtenir ces infos.

Cet api est très simple d'utilisation, pour la requête `GET http://www.omdbapi.com/?t=Zootopia&y=2016&plot=short&r=json` on obtient:

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

}```
