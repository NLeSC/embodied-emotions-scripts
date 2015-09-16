"""Helper functions to create dictionaries (lexicons).
"""
import requests
from bs4 import BeautifulSoup


def get_spelling_variants(term, categories, y_from, y_to):
    """Retrieve historic spelling variants from the INL Lexicon service.
    """
    # options for service:
    # get_wordforms
    # expand
    # get_lemma
    service = 'get_wordforms'

    url = 'http://sk.taalbanknederlands.inl.nl/LexiconService/lexicon/{s}'. \
          format(s=service)
    params = {
        'database': 'lexicon_service_db',
        'lemma': term,
        'year_from': y_from,
        'year_to': y_to
    }

    # Expand numbers to numbers by setting pos tag
    if '11' in categories:
        params['pos'] = 'NUM'

    r = requests.get(url, params=params)

    if r.status_code == requests.codes.ok:
        #print r.encoding
        r.encoding = 'utf-8'
        #print r.text
        soup = BeautifulSoup(r.text, 'xml')
        words = soup.find_all('found_wordforms')
        result = []
        for word in words:
            result.append(word.text)
        return result
    else:
        r.raise_for_status()
