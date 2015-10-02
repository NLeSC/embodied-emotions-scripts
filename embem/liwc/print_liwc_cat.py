#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to print all words in a LIWC category.

Usage: python print_liwc_cat.py <dictionary file> <category>

2014-11-18 j.vanderzwaan@esciencecenter.nl
"""
import argparse
import codecs
from embem.emotools.liwc_helpers import load_liwc

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dict_file', help='the name of the LIWC dictionary '
                        'file')
    parser.add_argument('liwc_cat', help='the name of the LIWC category to '
                        'print the words for')
    args = parser.parse_args()

    # Load liwc dict
    if args.dict_file.endswith('LIWC_Dutch_dictionary.dic'):
        encoding = 'latin1'
    else:
        encoding = 'utf8'

    liwc_dict, liwc_categories = load_liwc(args.dict_file, encoding)

    # Make dictionary of the form {liwc category: [word, word, word, ...]}
    liwc = {}
    for term, cats in liwc_dict.iteritems():
        for c in cats:
            cat = liwc_categories.get(c)
            if cat not in liwc.keys():
                liwc[cat] = []
            liwc[cat].append(term)

    cat = args.liwc_cat
    if liwc.get(cat):
        print 'LIWC words for {} ({} words)'.format(cat, len(liwc[cat]))
        print ' - '.join(liwc[cat])
    else:
        print 'Category "{}" not found in LIWC dictionary.'.format(cat)
