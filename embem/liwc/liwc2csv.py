#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to generate statistics on LIWC entities.

The script calculates how many LIWC words are found. Results are reported per
document.
This script can be used to compare the differences in numbers of words found
for the modern and historic versions of LIWC.
"""
from bs4 import BeautifulSoup
from lxml import etree
from collections import Counter
import argparse
import string
import glob
import pandas as pd

from embem.emotools.bs4_helpers import sentence, note, word
from embem.emotools.liwc_helpers import load_liwc


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_name', help='the name of the directory '
                        'containing the FoLiA XML files processed')
    parser.add_argument('dic', help='the liwc dictionary to be used')
    parser.add_argument('out_file', help='csv file to store the results')
    args = parser.parse_args()

    if args.dic.endswith('LIWC_Dutch_dictionary.dic'):
        encoding = 'latin1'
    else:
        encoding = 'utf8'

    liwc_dict, liwc_categories = load_liwc(args.dic, encoding)

    act_tag = '{http://ilk.uvt.nl/folia}div'
    event_tag = '{http://ilk.uvt.nl/folia}event'
    sentence_tag = '{http://ilk.uvt.nl/folia}s'
    word_tag = '{http://ilk.uvt.nl/folia}w'
    text_content_tag = '{http://ilk.uvt.nl/folia}t'

    result = pd.DataFrame(columns=liwc_categories.values()+['#words'])

    xml_files = glob.glob('{}/*.xml'.format(args.dir_name))

    for i, f in enumerate(xml_files):
        print '{} ({} of {})'.format(f, i+1, len(xml_files))
        num_words = 0
        liwc_count = Counter()

        # make sure all categories have a value in the DataFrame
        for cat in liwc_categories.values():
            liwc_count[cat] = 0

        text_id = f[-20:-7]

        fi = open(f)

        context = etree.iterparse(fi, events=('end',), tag=act_tag, huge_tree=True)
        for event, elem in context:
            #print elem.attrib
            if elem.get('class') == 'act':
                # load div into memory
                div_xml = BeautifulSoup(etree.tostring(elem), 'xml')
                sentences = div_xml.find_all(sentence)
                s = None
                for sent in sentences:
                    if not note(sent.parent):
                        sent_id = sent.attrs.get('xml:id')

                        sent_words = [w.t.string.lower()
                                      for w in sent.find_all(word)]
                        for w in sent_words:
                            if w not in string.punctuation:
                                num_words += 1
                            if w in liwc_dict.keys():
                                #print w
                                for cat in liwc_dict[w]:
                                    liwc_count[liwc_categories[cat]] += 1
        result.loc[text_id] = pd.Series(liwc_count)
        result.set_value(text_id, '#words', num_words)
    print result
    result.to_csv(args.out_file)
