"""Create data set for visualization assignment
The data set consists of:
<text id>\t<sentence id>\t<emotion label>\t<other label>\t<tagged words>

Usage: python folia2visualization-pairs.py <file in> <output dir>
Or: ./batch_do_python.sh folia2visualization-pairs.py <dir in> <output dir>
(for a directory containing folia files)
"""
from lxml import etree
from bs4 import BeautifulSoup
from embem.emotools.bs4_helpers import sentence, note
import argparse
import codecs
import os
from itertools import product


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='the name of the FoLiA XML file that '
                        'should be processed.')
    parser.add_argument('output_dir', help='the directory where the '
                        'generated text files should be saved')
    args = parser.parse_args()

    file_name = args.file
    output_dir = args.output_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # We are interested in labels/classes of the following three entity types:
    entity_classes = [u'EmbodiedEmotions-Level1', u'EmbodiedEmotions-Level2']

    act_tag = '{http://ilk.uvt.nl/folia}div'

    # Load document
    context = etree.iterparse(file_name, events=('end',), tag=act_tag)

    num_sent = 0
    num_emotional = 0
    sents = set()

    text_id = file_name[-20:-7]
    out_file = os.path.join(output_dir, '{}.txt'.format(text_id))
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
                        emotionLabels = []
                        otherLabels = []

                        for entity in sent.find_all('entity'):
                            e = entity.attrs.get('class')

                            # get emotion labels
                            if e.startswith('EmbodiedEmotions-EmotionLabel'):
                                emotionLabels.append(entity)

                            # get other relevant entities
                            for cl in entity_classes:
                                if e.startswith(cl):
                                    otherLabels.append(entity)
                                    #entity_words = [w.attrs.get('t')
                                    #                for w in entity.find_all('wref')]
                                    #ent_words = ' '.join(entity_words)

                                    #f.write(u'{}\t{}\t{}\n'.format(sent_id,
                                    #                               e,
                                    #                               ent_words))
                        if len(emotionLabels) > 0 and len(otherLabels) > 0:
                            p = product(emotionLabels, otherLabels)
                            for c in p:
                                ent1 = c[0]
                                label1 = ent1.attrs.get('class')
                                words1 = [w.attrs.get('t')
                                          for w in ent1.find_all('wref')]
                                ent2 = c[1]
                                label2 = ent2.attrs.get('class')
                                words2 = [w.attrs.get('t')
                                          for w in c[1].find_all('wref')]
                                if set(words1).issubset(words2) or set(words2).issubset(words1):
                                    if len(words1) < len(words2):
                                        ent_words = ' '.join(words1).lower()
                                    else:
                                        ent_words = ' '.join(words2).lower()
                                    l1 = label1.split(':')[1]
                                    l2 = label2.split(':')[1]
                                    f.write(u'{}\t{}\t{}\t{}\t{}\n'.format(
                                            text_id, sent_id, l1, l2,
                                            ent_words))
                                else:
                                    print 'Not subset!'
                                    print sent_id
                                    print words1
                                    print words2
                                    print ''
