#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Add LIWC words as entities in FoLiA XML file.
Usage: python add_liwc_entities.py <file in>
"""
from bs4 import BeautifulSoup
from datetime import datetime
import argparse
import codecs

from emotools import string_helpers


def add_entity(soup, sentence, cls, words):
    if sentence.find('entities'):
        entities = sentence.entities
    else:
        entities = soup.new_tag('entities')
        sentence.append(entities)

    entity = soup.new_tag('entity')
    entity['class'] = cls
    for w in words:
        entity.append(soup.new_tag('wref', id=w['xml:id'], t=w.t.string))

    entities.append(entity)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file_in', help='the name of the FoLiA XML file add '
                        'LIWC entities to')
    args = parser.parse_args()

    file_name = args.file_in

    # Load liwc dict
    with codecs.open('historic_Dutch_LIWC.dic', 'rb', 'utf8') as f:
        lines = f.readlines()

    liwc_dict = {}
    for line in lines:
        # word
        if line[0].isalpha():
            entry = line.split()
            term = entry[0]
            categories = entry[1:]
            liwc_dict[term] = categories

    # Load document
    # doc = folia.Document(file='medea-folia-no_events.xml')
    with open(file_name, 'r') as f:
        soup = BeautifulSoup(f, 'xml')

    words = soup.find_all('w')
    for word in words:
        w = word.t.string
        if w in liwc_dict.keys():
            # posemo
            if '13' in liwc_dict[w]:
                add_entity(soup, word.parent, 'liwc-posemo', [word])
            # negemo
            if '16' in liwc_dict[w]:
                add_entity(soup, word.parent, 'liwc-negemo', [word])

    annotation_tag = soup.new_tag('entity-annotation')
    annotation_tag['annotator'] = 'liwc'
    annotation_tag['annotatortype'] = 'auto'
    annotation_tag['datetime'] = datetime.now()
    annotation_tag['set'] = 'liwc-set'

    soup.annotations.append(annotation_tag)

    output_xml = soup.prettify("utf-8")
    with open('test.xml', 'w') as file:
        file.write(output_xml)
