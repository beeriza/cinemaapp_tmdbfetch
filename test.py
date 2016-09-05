from threading import Lock

import requests

from tmdb_movie_parser import TmdbMovieParser

j = requests.get(
    'https://storage.scrapinghub.com/items/62468/2/172?apikey=a2e488e0171345568c54d0d81c23669e&format=json').json()

l = Lock()


def print_movie(name):
    z = TmdbMovieParser().get_info(name)
    with l:
        print name
        if z:
            print z.get('eng_name'), z.get('release_year')


for i in j:
    print_movie(unicode(i['title']))
