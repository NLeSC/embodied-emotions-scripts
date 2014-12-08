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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_name', help='the name of the dir containing the '
                        'FoLiA XML files that should be processed.')
    args = parser.parse_args()

    dir_name = args.dir_name

    entity_class = u'EmbodiedEmotions'

    act_tag = '{http://ilk.uvt.nl/folia}div'

    os.chdir(dir_name)

    folia_counter = 0
    num_sent = 0
    num_emotional = 0
    stats = Counter()

    for file_name in os.listdir(dir_name):
        folia_counter += 1
        print '({}) {}'.format(folia_counter, file_name)

        sents = set()
        # load document
        context = etree.iterparse(file_name,
                                  events=('start', 'end'),
                                  tag=act_tag,
                                  huge_tree=True)
        delete = True
        for event, elem in context:
            if event == 'start' and elem.get('class') == 'act':
                delete = False
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
                                if e.startswith(entity_class):
                                    emotional = True
                                    stats[e] += 1
                            if emotional:
                                num_emotional += 1

                delete = True

            # clear memory
            #if delete:
            #    elem.clear()
            #    while elem.getprevious() is not None:
            #        del elem.getparent()[0]
            #        del context

    # print stats
    print '{} sentences in {} files'.format(num_sent, folia_counter)
    print '{} emotional sentences'.format(num_emotional)
    for tag, freq in stats.most_common():
        print '{}\t{}'.format(tag, freq)
