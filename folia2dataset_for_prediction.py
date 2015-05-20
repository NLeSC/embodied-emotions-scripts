"""Create multilabel data set to train embodied emotions classifiers
The data set consists of:
<sentence id>\t<sentence>\tEmotie_Liefde (embodied emotions labels separated by
_)
<sentence id>\t<sentence>\tNone ('None' if no words were tagged)

Usage: python folia2dataset_multiclass.py <file in> <output dir>
Or: ./batch_do_python.sh folia2dataset_multiclass.py <dir in> <output dir>
(for a directory containing folia files)
"""
from lxml import etree
from bs4 import BeautifulSoup
from emotools.bs4_helpers import sentence, note, word
import argparse
import codecs
import os
import gzip


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
    sentence_tag = '{http://ilk.uvt.nl/folia}s'

    # Load document
    if file_name.endswith('.gz'):
        fi = gzip.open(file_name)
    else:
        fi = file_name
    context = etree.iterparse(fi, events=('end',), tag=sentence_tag)

    num_sent = 0
    num_emotional = 0
    sents = set()

    if os.path.basename(file_name).startswith('F'):
        file_name = os.path.basename(file_name).replace('.xml.gz', '')
        file_name = os.path.basename(file_name).replace('.xml', '')
        out_file = os.path.join(output_dir, '{}.txt'.format(file_name))
    else:
        out_file = os.path.join(output_dir, '{}.txt'.format(file_name[-20:-7]))
    print 'Writing file: {}'.format(out_file)
    with codecs.open(out_file, 'wb', encoding='utf-8') as f:
        for event, elem in context:
            # load sentence into memory
            div_xml = BeautifulSoup(etree.tostring(elem), 'xml')
            sentences = div_xml.find_all(sentence)
            s = None
            for sent in sentences:
                if not note(sent.parent):
                    sent_id = sent.attrs.get('xml:id')
                    # use folia tokenization
                    sent_words = [w.t.string for w in sent.find_all(word)]
                    s = ' '.join(sent_words)

                    # remove duplicate sentences (mainly single word
                    # sentences indicating the speaker of a speaker turn,
                    # e.g., Medea.)
                    if s and s not in sents:
                        sents.add(s)
                        num_sent += 1

                        f.write(u'{}\t{}\t{}\n'.format(sent_id,
                                                       s,
                                                       'None'))

    print '{} sentences, {} emotional\n'.format(num_sent, num_emotional)
