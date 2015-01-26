#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to generate statistics on LIWC entities.

The script calculates how many LIWC words are found. This script can be used to
compare the differences in numbers of words found for the modern and historic
versions of LIWC.
"""
from bs4 import BeautifulSoup
from lxml import etree
from collections import Counter
import argparse
import string

from emotools.bs4_helpers import note, word
from emotools.liwc_helpers import load_liwc


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file_name', help='the name of the FoLiA XML file to '
                        'be processed')
    parser.add_argument('dic', help='the liwc dictionary to be used')
    args = parser.parse_args()

    if args.dic == 'LIWC_Dutch_dictionary.dic':
        encoding = 'latin1'
    else:
        encoding = 'utf8'

    liwc_dict, liwc_categories = load_liwc(args.dic, encoding)

    # Only words inside events are counted (this means title (i.e. words inside
    # heading tags) are not countes). This is also what is stored in
    # Elasticsearch. There are small differences between the total number of
    # words in ES and the total number of words as counted by this Script
    # (~tens of words difference). It is not clear why this is the case. It
    # probably has to do with the tokenizer (analyzer) used by ES vs. the
    # tokenizer used to generate the folia documents.
    act_tag = '{http://ilk.uvt.nl/folia}div'
    event_tag = '{http://ilk.uvt.nl/folia}event'
    sentence_tag = '{http://ilk.uvt.nl/folia}s'
    word_tag = '{http://ilk.uvt.nl/folia}w'
    text_content_tag = '{http://ilk.uvt.nl/folia}t'

    num_words = 0
    liwc_count = Counter()

    context = etree.iterparse(args.file_name,
                              events=('end',),
                              tag=event_tag,
                              huge_tree=True)

    for event, elem in context:
        # ignore subevents
        if not elem.getparent().tag == event_tag:
            event_xml = BeautifulSoup(etree.tostring(elem), 'xml')
            for element in event_xml.descendants:
                if word(element) and not note(element.parent.parent):
                    w = element.t.string.lower()
                    if w not in string.punctuation:
                        num_words += 1
                        if w in liwc_dict.keys():
                            #print w
                            for cat in liwc_dict[w]:
                                liwc_count[liwc_categories[cat]] += 1

    print 'Total # words\t{}\n'.format(num_words)
    print 'Category\tPercentage\tFrequency'
    cats = liwc_categories.values()
    cats.sort()
    for cat in cats:
        freq = liwc_count[cat]
        percentage = (freq/(num_words+0.0))*100
        print '{}\t{:.2f}\t{}'.format(cat, percentage, freq)
