#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from time import sleep
import json
import sys

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
    #ws =  get_spelling_variants('actueel', [], 1600, 1830)

    #print ws
    #for w in ws:
    #    print w.encode('utf-8')

    #sys.exit()
    with open('LIWC_Dutch_dictionary.dic', 'r') as f:
        lines = f.readlines()

    liwc_output = {}
    for line in lines:
        # legend
        if line[0].isdigit() or line.startswith(('%', '\r')):
            print line.strip()
        # word
        else:
            entry = line.split()
            term = entry[0]
            categories = entry[1:]
            t = term.decode('latin-1')
            words = get_spelling_variants(t, categories, 1600, 1830)
            words.append(t)
            #print term, words
            sleep(1)
            for word in words:
                if liwc_output.get(word) and not categories == liwc_output[word]:
                    new_c = list(set(categories + liwc_output.get(word)))
                    new_c.sort()
                    liwc_output[word] = new_c
                else:
                    liwc_output[word] = categories

    json.dumps(liwc_output, open('liwc_output.json','w'), sort_keys=True)
    #liwc_output = json.loads(open('liwc_output.json', 'r'), encoding='utf-8')

    entries = liwc_output.keys()
    entries.sort()
    for entry in entries:
        print '{e}\t\t{l}'.format(e=entry.encode('utf8'), l='\t'.join(liwc_output[entry]))
