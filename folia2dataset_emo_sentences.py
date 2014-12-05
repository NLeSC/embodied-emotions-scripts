"""Create a KAF file for each act in a FoLiA file
Usage: python folia2kaf.py <file in> <output dir>
"""
from lxml import etree
from bs4 import BeautifulSoup
from emotools.bs4_helpers import sentence, note
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='the name of the FoLiA XML file that '
                        'should be processed.')
    args = parser.parse_args()

    file_name = args.file

    entity_class = u'EmbodiedEmotions'

    act_tag = '{http://ilk.uvt.nl/folia}div'

    # Load document
    context = etree.iterparse(file_name, events=('end',), tag=act_tag)

    num_sent = 0
    num_emotional = 0
    sents = set()

    for event, elem in context:
        if elem.get('class') == 'act':
            # load act into memory
            act_xml = BeautifulSoup(etree.tostring(elem), 'xml')
            sentences = act_xml.find_all(sentence)
            s = None
            for sent in sentences:
                if not note(sent.parent):
                    num_sent += 1
                    # some t elements appear to be empty (this is not allowed,
                    # but it happens). So, check whether there is a string to
                    # add before adding it.
                    if sent.t:
                        if sent.t.string:
                            s = sent.t.string

                    entities = sent.find_all('entity')
                    emotional = False
                    for entity in entities:
                        if entity.attrs.get('class').startswith(entity_class):
                            emotional = True
                            break

                    if emotional:
                        num_emotional += 1

                    # write sentence to file
                    if s:
                        # remove duplicate sentences (mainly single word
                        # sentences indicating the speaker of a speaker turn,
                        # e.g., Medea.)
                        #if emotional and (s, int(emotional)) in sents:
                        #    print '-------------------->', s
                        sents.add((s, int(emotional)))

    num_emotional_set = 0
    for s, emotional in sents:
        print '{}\t{}'.format(s.encode('utf-8'), emotional)
        if emotional == 1:
            num_emotional_set += 1
    #print '#sentences in text: {}\n#emotional: {}'.format(num_sent, num_emotional)
    #print '#sentences in set: {}\n#emotional: {}'.format(len(sents), num_emotional_set)
