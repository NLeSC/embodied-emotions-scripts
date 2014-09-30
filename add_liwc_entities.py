#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Add LIWC words as entities in FoLiA XML file.
Usage: python add_liwc_entities.py <file in>
"""
from lxml import etree
from lxml.etree import Element
from bs4 import BeautifulSoup
from datetime import datetime
import argparse
import codecs
import os


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


def write_folia_file(context, folia_in, ext):
    head, tail = os.path.split(folia_in)
    p = tail.split('.')
    file_out = '{h}{s}{n}-{e}.xml'.format(n=p[0], h=head, s=os.sep, e=ext)
    with open(file_out, 'w') as f:
        f.write(etree.tostring(context.root,
                               encoding='utf8',
                               xml_declaration=True,
                               pretty_print=True))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file_in', help='the name of the FoLiA XML file add '
                        'LIWC entities to')
    args = parser.parse_args()

    file_name = args.file_in

    # Load liwc dict
    with codecs.open('historic_Dutch_LIWC.dic', 'rb', 'utf8') as f:
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

    # Load document
    context = etree.iterparse(file_name, events=('end',))
    annotations_tag = '{http://ilk.uvt.nl/folia}annotations'

    for event, elem in context:
        if elem.tag == annotations_tag:
            # add entity-annotation for liwc
            annotation_attrs = {
                'annotator': 'liwc',
                'annotatortype': 'auto',
                'datetime': datetime.now().isoformat(),
                'set': 'liwc-set'
            }
            annotation_elem = Element('entity-annotation', annotation_attrs)
            elem.append(annotation_elem)

    #words = soup.find_all('w')
    #for word in words:
    #    w = word.t.string
    #    if w in liwc_dict.keys():
    #        for cat in liwc_dict[w]:
    #            cat_label = 'liwc-{}'.format(liwc_categories[cat])
    #            add_entity(soup, word.parent, cat_label, [word])

    write_folia_file(context, file_name, 'liwc')
