#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Add LIWC words as entities in FoLiA XML file.
Usage: python add_liwc_entities.py <file in>
"""
from lxml import etree
from datetime import datetime
import argparse
import codecs
import os


def add_entity(sentence, cls, words, text_content_tag):
    entity_tag = '{http://ilk.uvt.nl/folia}entities'
    if sentence.find(entity_tag) is not None:
        entities = sentence.find(entity_tag)
    else:
        entities = etree.SubElement(sentence, 'entities')

    entity = etree.SubElement(entities, 'entity', {'class': cls})
    for w in words:
        wref_attrs = {
            'id': w.attrib.get('{http://www.w3.org/XML/1998/namespace}id'),
            't': w.find(text_content_tag).text
        }
        etree.SubElement(entity, 'wref', wref_attrs)


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
    context = etree.iterparse(file_name,
                              events=('end',),
                              remove_blank_text=True)
    annotations_tag = '{http://ilk.uvt.nl/folia}annotations'
    sentence_tag = '{http://ilk.uvt.nl/folia}s'
    word_tag = '{http://ilk.uvt.nl/folia}w'
    text_content_tag = '{http://ilk.uvt.nl/folia}t'

    for event, elem in context:
        if elem.tag == annotations_tag:
            # add entity-annotation for liwc
            annotation_attrs = {
                'annotator': 'liwc',
                'annotatortype': 'auto',
                'datetime': datetime.now().isoformat(),
                'set': 'liwc-set'
            }
            etree.SubElement(elem, 'entity-annotation', annotation_attrs)

        if elem.tag == sentence_tag:
            words = elem.findall(word_tag)
            for word in words:
                w = word.find(text_content_tag).text
                if w in liwc_dict.keys():
                    for cat in liwc_dict[w]:
                        cat_label = 'liwc-{}'.format(liwc_categories[cat])
                        add_entity(elem, cat_label, [word], text_content_tag)

    write_folia_file(context, file_name, 'liwc')
