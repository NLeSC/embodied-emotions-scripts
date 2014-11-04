#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract text from a folia xml file.
"""
import os
import argparse
import codecs
import sys
from lxml import etree
from bs4 import BeautifulSoup
from emotools.bs4_helpers import act, sentence, note


def act2text(act_xml):
    """Extract text from act.
    Returns a string that can be written to file.
    """
    text = []

    print 'act:', act_xml.find('div', 'act').attrs.get('xml:id')

    subacts = act_xml.find_all(act)

    # act_xml should contain exactly one act; if it contains more acts, these
    # acts are sub acts, that will be processed later
    if len(subacts) == 1:
        for elem in act_xml.descendants:
            if sentence(elem) and not note(elem.parent):
                # some t elements appear to be empty (this is not allowed, but
                # it happens). So, check whether there is a string to add
                # before adding it.
                if elem.t:
                    if elem.t.string:
                        text.append(elem.t.string)
    return text


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='the name of the directory '
                        'containing the FoLiA XML files that should be '
                        'processed')
    parser.add_argument('output_dir', help='the directory where the '
                        'generated text files should be saved')
    args = parser.parse_args()

    in_file = args.input_file
    output_dir = args.output_dir

    act_tag = '{http://ilk.uvt.nl/folia}div'

    # load document
    context = etree.iterparse(in_file,
                              events=('end',),
                              tag=act_tag,
                              huge_tree=True)

    text = []
    for event, elem in context:
        if elem.tag == act_tag and elem.get('class') == 'act':
            # load act into memory
            act_xml = BeautifulSoup(etree.tostring(elem), 'xml')
            text += act2text(act_xml)

    del context

    # write text to file
    out_file = os.path.join(output_dir, '{}.txt'.format(in_file[-20:-4]))
    print 'Writing file: {}'.format(out_file)
    with codecs.open(out_file, 'wb', encoding='utf-8') as f:
        f.write('\n'.join(text))
    print ''
