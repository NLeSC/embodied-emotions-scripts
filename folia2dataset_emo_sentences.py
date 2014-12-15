"""Create data set to train emotional sentence classifier file
The file contains (0=non-emotional, 1=emotional):
<sentence>\t{0,1}

Usage: python folia2dataset_emo_sentences.py <file in> <output dir>
Or: ./batch_do_python.sh folia2dataset_emo_sentences.py <dir in> <output dir>
(for a directory containing folia files)
"""
from lxml import etree
from bs4 import BeautifulSoup
from emotools.bs4_helpers import sentence, note, word
import argparse
import codecs
import os
import string


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='the name of the FoLiA XML file that '
                        'should be processed.')
    parser.add_argument('output_dir', help='the directory where the '
                        'generated text files should be saved')
    args = parser.parse_args()

    file_name = args.file
    output_dir = args.output_dir

    entity_class = u'EmbodiedEmotions'

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
                        # use folia tokenization
                        sent_words = [w.t.string for w in sent.find_all(word)]
                        s = ' '.join(sent_words)

                        # remove duplicate sentences (mainly single word
                        # sentences indicating the speaker of a speaker turn,
                        # e.g., Medea.)
                        if s and s not in sents:
                            sents.add(s)
                            num_sent += 1

                            entities = sent.find_all('entity')
                            emotional = False
                            for entity in entities:
                                e = entity.attrs.get('class')
                                if e.startswith(entity_class):
                                    emotional = True
                                    break

                            if emotional:
                                num_emotional += 1

                            f.write(u'{}\t{}\n'.format(s, int(emotional)))

    print '{} sentences, {} emotional\n'.format(num_sent, num_emotional)
