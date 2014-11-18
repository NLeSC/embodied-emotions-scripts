#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to print all words in a LIWC category.

Usage: python print_liwc_cat.py <dictionary file> <category>

2014-11-18 j.vanderzwaan@esciencecenter.nl
"""
import argparse
import codecs


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dict_file', help='the name of the LIWC dictionary '
                        'file')
    parser.add_argument('liwc_cat', help='the name of the LIWC category to '
                        'print the words for')
    args = parser.parse_args()

    # Load liwc dict
    with codecs.open(args.dict_file, 'rb', 'latin1') as f:
        lines = f.readlines()

    liwc_categories = {}
    liwc_dict = {}

    for line in lines:
        # LIWC category
        if line[0].isdigit():
            entry = line.split()
            # remove 0 from strings like 01
            c = str(int(entry[0]))
            liwc_categories[c] = entry[1]
        # word
        elif line[0].isalpha():
            entry = line.split()
            term = entry[0]
            categories = entry[1:]
            liwc_dict[term] = categories

    # Make dictionary of the form {liwc category: [word, word, word, ...]}
    liwc = {}
    for term, cats in liwc_dict.iteritems():
        for c in cats:
            cat = liwc_categories.get(c)
            if cat not in liwc.keys():
                liwc[cat] = []
            liwc[cat].append(term)

    cat = args.liwc_cat.lower()
    if liwc.get(cat):
        print 'LIWC words for {} ({} words)'.format(cat, len(liwc[cat]))
        print ' - '.join(liwc[cat])
    else:
        print 'Category "{}" not found in LIWC dictionary.'.format(cat)
