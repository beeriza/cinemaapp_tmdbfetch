# -*- coding: cp1255 -*-
import requests
import datetime
import re
from imdb import IMDb
import itertools
api_key = '546a1e3c91bafcbaccfa4fcae533738c'
image_tmdb_path = 'https://image.tmdb.org/t/p/w300'
youtube_trailer_path = 'https://www.youtube.com/watch?v='
fake_time = datetime.datetime(1,1,1)
bad_words = ('3D',u'עברית',u'רוסית',u'תלת',u'מדובב')



def get_tmdb_movie_info_by_name(movie_name):
    tmdb_data ={}
    search_url = 'http://api.themoviedb.org/3/search/movie'
    payload = {'api_key': api_key, 'query': movie_name,'include_adult':'false'}
    search_request = requests.get(search_url,params=payload)
    search_json_results = search_request.json()['results']
    if not search_json_results:
        return
    search_json_results_sorted = sorted(search_json_results, key=lambda k: datetime.datetime.strptime(k.get('release_date'),'%Y-%m-%d') if k.get('release_date') != '' else fake_time)

    # Take latest movie
    latest_movie_tmdb_id = search_json_results_sorted[-1]['id']

    movie_url = 'http://api.themoviedb.org/3/movie/{}'.format(latest_movie_tmdb_id)
    payload = {'api_key': api_key, 'id': latest_movie_tmdb_id,'language':'he-IL'}
    movie_request = requests.get(movie_url,params=payload)
    movie_json = movie_request.json()
    
    tmdb_data['heb_name'] = movie_json['title']
    tmdb_data['eng_name'] = movie_json['original_title']
    tmdb_data['imdb_id'] = movie_json['imdb_id']
    tmdb_data['poster_link'] = image_tmdb_path + movie_json['poster_path']
    tmdb_data['genre_heb'] = ','.join(genre['name'] for genre in movie_json['genres'])
    movie_trailer_url = 'http://api.themoviedb.org/3/movie/{}/videos'.format(latest_movie_tmdb_id)
    payload = {'api_key': api_key, 'id': latest_movie_tmdb_id}
    movie_trailer_request = requests.get(movie_trailer_url,params=payload)
    movie_trailer_json = movie_trailer_request.json()['results']
    movie_trailer_path = ''
    if movie_trailer_json:
        for movie_trailer in movie_trailer_json:
            if movie_trailer['type'].lower() == 'trailer' and movie_trailer['site'].lower() == 'youtube':
                if movie_trailer['iso_3166_1'] == 'IL' and movie_trailer['iso_639_1'] == 'he':
                    tmdb_data['movie_trailer_path'] = youtube_trailer_path + movie_trailer['key']
                    break
                elif movie_trailer['iso_3166_1'] == 'US' and movie_trailer['iso_639_1'] == 'en':
                    tmdb_data['movie_trailer_path'] = youtube_trailer_path + movie_trailer['key']

    im = IMDb()
    
    tmdb_data['imdb_rank'] = im.get_movie(re.sub('\D', '', tmdb_data['imdb_id'])).get('rating')


    return tmdb_data

def get_tmdb_info_by_cinema_name(movie_name):
    tmdb_data = get_tmdb_movie_info_by_name(movie_name)
    if tmdb_data:
        return tmdb_data

    movie_name_no_spc = ' '.join(movie_name.split())

    # Find bad words in movie    
    movie_name_no_spc_spl = movie_name_no_spc.split()
    bad_words_in_movie = [movie_word for movie_word in movie_name_no_spc_spl for bad_word in bad_words if bad_word in movie_word]

    # Match by exact word, will not work with לרוסית if the word is רוסית
    #set_bad_words = set(bad_words)
    #set_movie_name_no_spc_spl = set(movie_name_no_spc_spl)
    # = set_bad_words.intersection(set_movie_name_no_spc_spl)

    # Create bad words combinations 
    bad_words_in_movie_combinations = [c for i in range(len(bad_words_in_movie)) for c in itertools.combinations(bad_words_in_movie, i+1)]

    movie_name_no_spc_orig = movie_name_no_spc
    for bad_word_comb in bad_words_in_movie_combinations:
        movie_name_no_spc = reduce(lambda m,b : m.replace(b,''),bad_word_comb,movie_name_no_spc)
        movie_name_no_spc = ' '.join(movie_name_no_spc.split())
        tmdb_data = get_tmdb_movie_info_by_name(movie_name_no_spc)
        if tmdb_data:
            tmdb_data['bad_words'] = bad_word_comb
            return tmdb_data
        movie_name_no_spc = movie_name_no_spc_orig
        
    return None

import pprint
pprint.pprint(get_tmdb_info_by_cinema_name(u'ice age 3 3D רוסית מדובב לעברית'))
