#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Add LIWC words as entities in FoLiA XML file.
Usage: python add_liwc_entities.py <file in> <dir out>
"""
from lxml import etree
from datetime import datetime
import argparse
import codecs

from emotools.folia_helpers import add_entity, write_folia_file


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file_in', help='the name of the FoLiA XML file add '
                        'LIWC entities to')
    parser.add_argument('dir_out', help='the name of the directory to save '
                        'the output file to')
    args = parser.parse_args()

    file_name = args.file_in
    dir_out = args.dir_out

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

    write_folia_file(context, file_name, dir_out, 'liwc')
