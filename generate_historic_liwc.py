#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from time import sleep
import json
import sys
import codecs

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
        words = soup.find_all('wordform')
        result = []
        for word in words:
            result.append(word.text)
        return result
    else:
        r.raise_for_status()


if __name__ == '__main__':
    # read file and convert byte strings to unicode
    with codecs.open('LIWC_Dutch_dictionary.dic', 'rb', 'latin-1') as f:
        lines = f.readlines()

    liwc_category_output = []
    liwc_output = {}
    for line in lines:
        # legend
        if line[0].isdigit() or line.startswith(('%', '\r')):
            liwc_category_output.append(line.strip())
        # word
        else:
            entry = line.split()
            term = entry[0]
            categories = entry[1:]
            sleep(1)
            words = get_spelling_variants(term, categories, 1600, 1830)
            words.append(term)
            print term, words
            for word in words:
                if liwc_output.get(word) and not categories == liwc_output[word]:
                    new_c = list(set(categories + liwc_output.get(word)))
                    new_c.sort()
                    liwc_output[word] = new_c
                else:
                    liwc_output[word] = categories

    with codecs.open('liwc_output.json', 'w', 'utf8') as f:
        json.dump(liwc_output, f, sort_keys=True, ensure_ascii=False, indent=2)
    
    #with codecs.open('liwc_output.json', 'rb', 'utf8') as f:
    #    liwc_output = json.load(f, encoding='utf-8')

    with codecs.open('historic_Dutch_LIWC.dic', 'wb', 'utf8') as f:
        f.write('\n'.join(liwc_category_output))
        
        entries = liwc_output.keys()
        entries.sort()
        for entry in entries:
            f.write(entry)
            f.write('\t\t')
            f.write('\t'.join(liwc_output[entry]))
            f.write('\n')
