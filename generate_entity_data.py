#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to generate text files containing LIWC and EmbEm entities.

Ouptut format: <word id>\t<word>\t<entity category>

The script writes 3 files:
1. embem entities: embem_data.csv
2. historic liwc: liwc_hist_data.csv
3. modern liwc: liwc_modern_data.csv

Output is appended to these three files (with the batch script).

Usage: python generate_entity_data.py <folia xml> <output dir>
Or: ./batch_do_python.sh <folia dir> <output dir>
"""
from bs4 import BeautifulSoup
from lxml import etree
import argparse
import string
import codecs

from emotools.bs4_helpers import note, word, sentence
from emotools.liwc_helpers import load_liwc


def liwc_entity_str(liwc_dict, liwc_cats, relevant_cats, w, w_id):
    result = []
    if w in liwc_dict.keys():
        for cat in liwc_dict[w]:
            c = liwc_cats[cat]
            if c in relevant_cats:
                #print w, c
                result.append(u'{}\t{}\t{}\n'.format(w_id, w, c))
    return ''.join(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file_name', help='the name of the FoLiA XML file to '
                        'be processed')
    parser.add_argument('out_dir', help='the name of the directory to write '
                        'the output to')
    args = parser.parse_args()

    liwc_dict_m, liwc_cats = load_liwc('LIWC_Dutch_dictionary.dic', 'latin1')
    liwc_dict_h, liwc_cats = load_liwc('historic_Dutch_LIWC.dic', 'utf8')

    relevant_cats = ['Posemo', 'Negemo', 'Body', 'Physcal', 'Anger', 'Sad']
    #relevant_cats = ['Body', 'Physcal', 'Anger', 'Sad']

    # We are interested in labels/classes of the following three entity types:
    entity_classes = [u'EmbodiedEmotions-Level1', u'EmbodiedEmotions-Level2',
                      u'EmbodiedEmotions-EmotionLabel']

    liwc_data_m = []
    liwc_data_h = []
    embem_data = []

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

    context = etree.iterparse(args.file_name,
                              events=('end',),
                              tag=event_tag,
                              huge_tree=True)

    for event, elem in context:
        # ignore subevents
        if not elem.getparent().tag == event_tag:
            event_xml = BeautifulSoup(etree.tostring(elem), 'xml')
            for element in event_xml.descendants:
                if sentence(element) and not note(element.parent):
                    entities = element.find_all('entity')
                    classes = []
                    for entity in entities:
                        e = entity.attrs.get('class')
                        for cl in entity_classes:
                            if e.startswith(cl):
                                label = e.split(':')[1]
                                wrefs = entity.find_all('wref')
                                for wref in wrefs:
                                    w_id = wref.get('id')
                                    w = wref.get('t').lower()
                                    line = u'{}\t{}\t{}\n'.format(w_id, w, label)
                                    embem_data.append(line)

                elif word(element) and not note(element.parent.parent):
                    w_id = element.get('xml:id')
                    w = element.t.string.lower()
                    if w not in string.punctuation:
                        # modern LIWC
                        e = liwc_entity_str(liwc_dict_m, liwc_cats,
                                            relevant_cats, w, w_id)
                        if e:
                            liwc_data_m.append(e)
                        # historic LIWC
                        e = liwc_entity_str(liwc_dict_h, liwc_cats,
                                            relevant_cats, w, w_id)
                        if e:
                            liwc_data_h.append(e)
    # write results to file
    out_file = '{}/liwc_modern_data.csv'.format(args.out_dir)
    with codecs.open(out_file, 'ab', 'utf8') as f:
        f.write(''.join(liwc_data_m))

    out_file = '{}/liwc_hist_data.csv'.format(args.out_dir)
    with codecs.open(out_file, 'ab', 'utf8') as f:
        f.write(''.join(liwc_data_h))
        #for line in liwc_data_h:
        #    f.write(line)
        #    f.write('\n')

    out_file = '{}/embem_data.csv'.format(args.out_dir)
    with codecs.open(out_file, 'ab', 'utf8') as f:
        f.write(''.join(embem_data))
