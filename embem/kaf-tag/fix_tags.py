"""Script that generates a tag file with new word ids
Usage: python fix_tags.py <folia-file> <tag file> <dir to save new tag file to>
Or use in bash script:
./batch_fix_tags.sh <dir with folia-files> <dir with tag-files dirs>
<dir to save new tag-files in>

20141209 j.vanderzwaan@esciencecenter.nl
"""

import codecs
from lxml import etree
from bs4 import BeautifulSoup
from embem.emotools.bs4_helpers import word
import argparse
import os
import re
import sys


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folia', help='the name of the FoLiA XML file that '
                        'contains the correct word ids')
    parser.add_argument('tag', help='the name of the tag file that '
                        'contains incorrect word ids')
    parser.add_argument('output_dir', help='the directory where the new tag '
                        'files should be saved')
    args = parser.parse_args()

    folia = args.folia
    tag = args.tag
    out_dir = args.output_dir

    _d, file_name = os.path.split(tag)
    out_file = os.path.join(out_dir, file_name)

    #print 'Saving file to', out_file

    # lees tag file in geheugen
    with codecs.open(tag, 'rb', 'utf-8') as f:
        tag_lines = f.readlines()
    print '\tFound {} tags'.format(len(tag_lines))
    tags = iter(tag_lines)

    curr_tag = None
    # word ids that start with lg-added must be replaced
    reg = r'^lg-added-\d+'

    word_tag = '{http://ilk.uvt.nl/folia}w'

    # Load folia document
    context = etree.iterparse(folia, events=('end',), tag=word_tag)

    found = 0

    # open file for output
    with codecs.open(out_file, 'wb', 'utf-8') as f:
        for event, elem in context:
            if not curr_tag:
                try:
                    curr_tag = tags.next()

                    parts = curr_tag.split('\t')
                    tag_id = parts[0]
                    tag_word = parts[1]

                    #print 'looking for', tag_id
                except StopIteration:
                    print '\tTranslated {} tags'.format(found)
                    sys.exit()

            if event == 'end':
                word_xml = BeautifulSoup(etree.tostring(elem), 'xml')
                w = word_xml.find(word)
                w_id = w.attrs.get('xml:id')
                w_word = w.t.string

                match_part = re.sub(reg, '', tag_id)
                if w_id.endswith(match_part) and w_word == tag_word:
                    found += 1
                    #print 'found match:'
                    #print w_id, w_word
                    #print tag_id, tag_word
                    #print '{}\t{}'.format(w_id, '\t'.join(parts[1:]).encode('utf-8'))
                    f.write('{}\t{}'.format(w_id, '\t'.join(parts[1:]).encode('utf-8')).decode('utf-8'))
                    curr_tag = None
