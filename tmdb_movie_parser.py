# -*- coding: cp1255 -*-
import datetime
import itertools
import re

import requests
from imdb import IMDb

GOOGLE_SUGGESTIONS_URL = "http://suggestqueries.google.com/complete/search?client=firefox&q="

API_KEY = '546a1e3c91bafcbaccfa4fcae533738c'

TMDB_API_MOVIE_SEARCH_URL = 'http://api.themoviedb.org/3/search/movie'
IMAGE_TMDB_PATH = 'https://image.tmdb.org/t/p/w300'
TMDB_API_MOVIE_DETAILS_URL = 'http://api.themoviedb.org/3/movie/'

YOUTUBE_TRAILER_PATH = 'https://www.youtube.com/watch?v='
FAKE_TIME = datetime.datetime(1, 1, 1)
BAD_WORDS = {'3D', u'עברית', u'רוסית', u'תלת', u'מדובב'}


class TmdbMovieParser:
    def __init__(self):
        pass

    def get_info(self, movie_name):
        for possible_movie_name, show_type in self._generate_possible_movie_names(movie_name):
                tmdb_data = self._get_movie_details(possible_movie_name)
                if tmdb_data:
                    tmdb_data['show_type'] = show_type
                    return tmdb_data

    def _generate_possible_movie_names(self, movie_name):
        yield (movie_name, 'Normal')
        for bad_word_comb in self._get_bad_words_combinations(movie_name):
            yield (self._clear_bad_words(bad_word_comb, movie_name), bad_word_comb)

        for bad_word_comb in self._get_bad_words_combinations(movie_name):
            google_suggest = self._google_suggest(self._clear_bad_words(bad_word_comb, movie_name))
            if google_suggest:
                for suggest in google_suggest:
                    yield (suggest, 'Normal')
        google_suggest = self._google_suggest(movie_name)
        if google_suggest:
            for suggest in google_suggest:
                yield (suggest, 'Normal')

    def _google_suggest(self, name):
        try:
            return requests.get(GOOGLE_SUGGESTIONS_URL + name).json()[1]
        except IndexError:
            return None

    def _clear_bad_words(self, bad_word_comb, movie_name):
        return reduce(lambda m, b: m.replace(b, ''), bad_word_comb, movie_name)

    def _get_bad_words_combinations(self, movie_name):
        bad_words_in_movie = self._get_bad_words_in_movie_name(movie_name)
        return [c for i in range(len(bad_words_in_movie)) for c in itertools.combinations(bad_words_in_movie, i + 1)]

    def _get_bad_words_in_movie_name(self, movie_name):
        movie_name_words = movie_name.split()
        return [movie_word for movie_word in movie_name_words for bad_word in BAD_WORDS
                if bad_word in movie_word]

    def _get_movie_details(self, movie_name):
        movie_tmdb_id = self._get_tmdb_movie_id_search_result(movie_name)
        if not movie_tmdb_id:
            return None
        payload = {'api_key': API_KEY, 'id': movie_tmdb_id, 'language': 'he-IL'}
        movie_json = requests.get(TMDB_API_MOVIE_DETAILS_URL + str(movie_tmdb_id), params=payload).json()
        return {'heb_name': movie_json['title'],
                'eng_name': movie_json['original_title'],
                'imdb_id': movie_json['imdb_id'],
                'genre_heb': self._parse_genres(movie_json),
                'movie_trailer_path': self._get_movie_trailer_path(movie_tmdb_id),
                'overview': movie_json['overview'],
                'imdb_rank': self._get_imdb_rating(movie_json['imdb_id']),
                'release_year': self._get_release_date_from_tmdb_result(movie_json).year}

    def _get_tmdb_movie_id_search_result(self, movie_name):
        payload = {'api_key': API_KEY, 'query': self._remove_extra_spaces(movie_name), 'include_adult': 'false'}
        tmdb_result = requests.get(TMDB_API_MOVIE_SEARCH_URL, params=payload).json()['results']
        return self._get_most_relevant_movie_id_from_tmdb_result(tmdb_result) if tmdb_result else None

    def _get_most_relevant_movie_id_from_tmdb_result(self, tmdb_search_result):
        most_relevant_movie = max(tmdb_search_result, key=self._get_release_date_from_tmdb_result)
        if self._get_release_date_from_tmdb_result(most_relevant_movie).year < datetime.date.today().year - 2:
            return None
        return most_relevant_movie['id']

    def _get_release_date_from_tmdb_result(self, tmdb_result):
        if tmdb_result.get('release_date') != '':
            return datetime.datetime.strptime(tmdb_result.get('release_date'), '%Y-%m-%d')
        return FAKE_TIME

    def _parse_genres(self, movie_json):
        return ','.join(map(lambda g: g["name"], movie_json['genres']))

    def _get_imdb_rating(self, imdb_id):
        return IMDb().get_movie(re.sub('\D', '', imdb_id)).get('rating')

    def _get_movie_trailer_path(self, movie_tmdb_id):
        movie_trailer_path = None
        movie_trailer_url = 'http://api.themoviedb.org/3/movie/{}/videos'.format(movie_tmdb_id)
        payload = {'api_key': API_KEY, 'id': movie_tmdb_id}
        movie_trailer_json = requests.get(movie_trailer_url, params=payload).json()['results']
        if not movie_trailer_json:
            return None
        for movie_trailer in filter(self._is_youtube_trailer, movie_trailer_json):
            if self._is_hebrew_trailer(movie_trailer):
                return YOUTUBE_TRAILER_PATH + movie_trailer['key']
            elif self._is_english_trailer(movie_trailer):
                movie_trailer_path = YOUTUBE_TRAILER_PATH + movie_trailer['key']
        return movie_trailer_path

    def _is_youtube_trailer(self, movie_trailer_data):
        return movie_trailer_data['type'].lower() == 'trailer' and movie_trailer_data['site'].lower() == 'youtube'

    def _is_hebrew_trailer(self, movie_trailer_data):
        return movie_trailer_data['iso_3166_1'] == 'IL' and movie_trailer_data['iso_639_1'] == 'he'

    def _is_english_trailer(self, movie_trailer_data):
        return movie_trailer_data['iso_3166_1'] == 'US' and movie_trailer_data['iso_639_1'] == 'en'

    def _remove_extra_spaces(self, movie_name):
        return ' '.join(movie_name.split())
