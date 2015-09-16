#!/usr/bin/env python
# -.*- coding: utf-8 -.*-
"""Script to save text in xml file(s) to text file(s).

Usage: debates2txt.py <xml-file or directory containing xml files>

2014-12-15 j.vanderzwaan@esciencecenter.nl
"""
import argparse
import xml.etree.ElementTree as ET
import re
import os
import codecs


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('xml', help='the name of the xml file containing the '
                        'the word field counts should be extracted for')
    args = parser.parse_args()

    # file or directory?
    if os.path.isfile(args.xml):
        files = [args.xml]
    else:
        files = []
        for fn in os.listdir(args.xml):
            file_name = '{}{}{}'.format(args.xml, os.sep, fn)
            if os.path.isfile(file_name):
                files.append(file_name)

    for input_file in files:
        # read xml file
        tree = ET.parse(input_file)
        root = tree.getroot()

        lines = []
        for speech in tree.getiterator('speech'):
            speaker = speech.attrib.get('speaker')
            text = ET.tostring(speech)

            # remove xml tags
            text = re.sub('<[^>]*>', '', text)
            # remove html entities (e.g., &#611;)
            text = re.sub('&#\d+;', '', text)

            lines.append(text)
        _head, tail = os.path.split(input_file)
        print tail
        out_file = '{}.txt'.format(tail.split('.')[0])
        with codecs.open(out_file, 'wb', 'utf-8') as f:
            f.write('\n'.join(lines))
            

