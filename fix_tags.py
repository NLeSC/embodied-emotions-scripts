import codecs
from lxml import etree
from bs4 import BeautifulSoup
from emotools.bs4_helpers import act, sentence, word, speaker_turn, note
import argparse
import os
import re
import sys


if __name__ == '__main__':
    folia = '/home/jvdzwaan/data/embem-annotatie/vinc001pefr02_01.xml'
    tag = '/home/jvdzwaan/data/embem-annotatie-tag-fix/vinc001pefr02/vinc001pefr02_01__act-01.tag'
    #tag = '/home/jvdzwaan/data/kaf2folia/vinc001pefr02/vinc001pefr02_01__act-01.tag'
    out_dir = '/home/jvdzwaan/data/embem-annotatie-tag-fix/'

    d, file_name = os.path.split(tag)
    out_file = os.path.join(out_dir, file_name)

    print 'Saving file to', out_file

    # lees tag file in geheugen
    with codecs.open(tag, 'rb', 'utf-8') as f:
        tag_lines = f.readlines()
    print 'Found {} tags'.format(len(tag_lines))
    tags = iter(tag_lines)

    curr_tag = None
    # word ids that start with lg-added must be replaced
    reg = r'^lg-added-\d+'

    word_tag = '{http://ilk.uvt.nl/folia}w'

    # Load folia document
    context = etree.iterparse(folia, events=('end',), tag=word_tag)

    # open file for output
    with codecs.open(out_file, 'wb', 'utf-8') as f:
        for event, elem in context:
            if not curr_tag:
                try:
                    curr_tag = tags.next()

                    parts = curr_tag.split('\t')
                    tag_id = parts[0]
                    tag_word = parts[1]

                    print 'looking for', tag_id
                except StopIteration:
                    sys.exit()

            if event == 'end':
                word_xml = BeautifulSoup(etree.tostring(elem), 'xml')
                w = word_xml.find(word)
                w_id = w.attrs.get('xml:id')
                w_word = w.t.string

                match_part = re.sub(reg, '', tag_id)
                #if re.match(reg, tag_id):
                #    print 'tag_id matches regex', tag_id, w_id
                if w_id.endswith(match_part) and w_word == tag_word:
                    print 'found match:'
                    print w_id, w_word
                    print tag_id, tag_word
                    #print '{}\t{}'.format(w_id, '\t'.join(parts[1:]).encode('utf-8'))
                    f.write('{}\t{}'.format(w_id, '\t'.join(parts[1:]).encode('utf-8')).decode('utf-8'))
                    curr_tag = None
