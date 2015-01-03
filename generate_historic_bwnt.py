#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import sleep
import json
import codecs
from emotools.lexicon import get_spelling_variants


if __name__ == '__main__':
    # read file and convert byte strings to unicode
    with codecs.open('BWNT05_v003.txt', 'rb', 'latin-1') as f:
        lines = f.readlines()

    count = 0

    spelling_vars = {}
    for line in lines:
        count += 1
        entry = line.split(';')
        # lexicon service needs lower case input
        term = entry[3].lower()
        term = term.replace('"', '')
        #sleep(0.3)
        words = get_spelling_variants(term, [], 1600, 1830)
        words = list(set(words))

        if len(words) > 0:
            spelling_vars[term] = words

        if count % 1000 == 0:
            print count

        print term, words

    # write spelling variants to file
    with codecs.open('bwnt_spelling_variants.json', 'w', 'utf8') as f:
        json.dump(spelling_vars, f, sort_keys=True, ensure_ascii=False,
                  indent=2)
