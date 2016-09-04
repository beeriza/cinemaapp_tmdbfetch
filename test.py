import requests
from tmdb_movie_parser import TmdbMovieParser

j = requests.get(
    'https://storage.scrapinghub.com/items/62468/2/172?apikey=a2e488e0171345568c54d0d81c23669e&format=json').json()

for i in j:
    z = TmdbMovieParser().get_tmdb_info_by_cinema_name(unicode(i['title']))
    print i['title']
    if z:
        print z.get('eng_name')
