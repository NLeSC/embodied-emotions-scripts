"""Create data set for visualization assignment
The data set consists of:
<sentence id>\t<label>\t<tagged words>

Usage: python folia2visualization.py <file in> <output dir>
Or: ./batch_do_python.sh folia2visualization.py <dir in> <output dir>
(for a directory containing folia files)
"""
from lxml import etree
from bs4 import BeautifulSoup
from emotools.bs4_helpers import sentence, note
import argparse
import codecs
import os


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='the name of the FoLiA XML file that '
                        'should be processed.')
    parser.add_argument('output_dir', help='the directory where the '
                        'generated text files should be saved')
    args = parser.parse_args()

    file_name = args.file
    output_dir = args.output_dir

    # We are interested in labels/classes of the following three entity types:
    entity_classes = [u'EmbodiedEmotions-Level1', u'EmbodiedEmotions-Level2',
                      u'EmbodiedEmotions-EmotionLabel']

    act_tag = '{http://ilk.uvt.nl/folia}div'

    # Load document
    context = etree.iterparse(file_name, events=('end',), tag=act_tag)

    num_sent = 0
    num_emotional = 0
    sents = set()

    out_file = os.path.join(output_dir, '{}.txt'.format(file_name[-20:-7]))
    print 'Writing file: {}'.format(out_file)
    with codecs.open(out_file, 'wb', encoding='utf-8') as f:
        for event, elem in context:
            if elem.get('class') == 'act':
                # load act into memory
                act_xml = BeautifulSoup(etree.tostring(elem), 'xml')
                sentences = act_xml.find_all(sentence)
                s = None
                for sent in sentences:
                    if not note(sent.parent):
                        sent_id = sent.attrs.get('xml:id')

                        for entity in sent.find_all('entity'):
                            e = entity.attrs.get('class')
                            for cl in entity_classes:
                                if e.startswith(cl):
                                    entity_words = [w.attrs.get('t')
                                                    for w in entity.find_all('wref')]
                                    ent_words = ' '.join(entity_words)

                                    f.write(u'{}\t{}\t{}\n'.format(sent_id,
                                                                   e,
                                                                   ent_words))
