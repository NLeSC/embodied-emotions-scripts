#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import sleep
import json
import codecs
from emotools.lexicon import get_spelling_variants
import pandas as pd


if __name__ == '__main__':
    # read file and convert byte strings to unicode
    with codecs.open('SWN-NL-voor-Janneke.txt', 'rb', 'latin1') as f:
        lines = f.readlines()

    count = 0

    spelling_vars = {}
    for line in lines:
        count += 1
        entry = line.split(';')
        # lexicon service needs lower case input
        term = entry[0].lower()
        term = term.replace('"', '')
        while True:
            try:
                sleep(1)
                words = get_spelling_variants(term, [], 1600, 1830)
                words = list(set(words))
                break
            except:
                print 'Retry!'
                sleep(5)
                pass

        if len(words) > 0:
            spelling_vars[term] = words

        if count % 1000 == 0:
            print count

        print term, words

    # write spelling variants to file
    with codecs.open('swn-nl_spelling_variants.json', 'w', 'utf8') as f:
        json.dump(spelling_vars, f, sort_keys=True, ensure_ascii=False,
                  indent=2)
