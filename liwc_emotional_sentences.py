"""Count the numbers of annotated entities and emotional sentences in the
corpus that was manually annotated.

Usage: python annotation_statistics.py <dir containing the folia files with
EmbodiedEmotions annotations>
"""
from lxml import etree
from bs4 import BeautifulSoup
from emotools.bs4_helpers import sentence, note
import argparse
import os
from collections import Counter
import json
import codecs

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_name', help='the name of the dir containing the '
                        'FoLiA XML files that should be processed.')
    args = parser.parse_args()

    dir_name = args.dir_name

    act_tag = '{http://ilk.uvt.nl/folia}div'

    cur_dir = os.getcwd()
    os.chdir(dir_name)

    folia_counter = 0
    num_sent = 0
    num_emotional = 0
    stats = Counter()
    entity_words = {}
    text_stats = {}
    emotional_cats = ['liwc-Posemo', 'liwc-Negemo']

    print 'Files'
    for file_name in os.listdir(dir_name):
        folia_counter += 1
        print '{}'.format(file_name)

        text_id = file_name[0:13]
        text_stats[text_id] = Counter()

        sents = set()
        # load document
        context = etree.iterparse(file_name,
                                  events=('start', 'end'),
                                  tag=act_tag,
                                  huge_tree=True)
        for event, elem in context:
            if event == 'end' and elem.get('class') == 'act':
                # load act into memory
                act_xml = BeautifulSoup(etree.tostring(elem), 'xml')
                sentences = act_xml.find_all(sentence)
                s = None
                for sent in sentences:
                    if not note(sent.parent):
                        # some t elements appear to be empty (this is not
                        # allowed, but it happens). So, check whether there is
                        # a string to add before adding it.
                        if sent.t:
                            if sent.t.string:
                                s = sent.t.string

                        # calculate stats only for unique sentences in text
                        if s and s not in sents:
                            sents.add(s)
                            num_sent += 1

                            entities = sent.find_all('entity')
                            emotional = False
                            for entity in entities:
                                e = entity.attrs.get('class')
                                if e in emotional_cats:
                                    emotional = True

                            if emotional:
                                num_emotional += 1

        del context
            # clear memory
            # results in segmentation fault (for some reason)
            #if delete:
            #    elem.clear()
            #    while elem.getprevious() is not None:
            #        del elem.getparent()[0]
            #        del context

    # print stats
    print '\nBasic stats'
    print '{} sentences in {} files'.format(num_sent, folia_counter)
    perc = float(num_emotional)/float(num_sent)*100.0
    print '{} emotional sentences ({:.2f}%)'.format(num_emotional, perc)