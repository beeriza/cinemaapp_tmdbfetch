# coding=utf-8
from threading import Lock

import requests

from tmdb_movie_parser import TmdbMovieParser


def print_movie(name):
    z = TmdbMovieParser().get_info(name)
    print name
    if z:
        print z


# j = requests.get(
#     'https://storage.scrapinghub.com/items/62468/2/172?apikey=a2e488e0171345568c54d0d81c23669e&format=json').json()
# for i in j:
#     print_movie(unicode(i['title']))

print_movie(u"החיים הסודיים של החיות 3D")
