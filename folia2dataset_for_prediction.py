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


def write_sentence(sent_id, sent_words, sents, f, num_sent):
    s = unicode(' '.join(sent_words))
    # remove duplicate sentences (mainly single word
    # sentences indicating the speaker of a speaker turn,
    # e.g., Medea.)
    s = s.strip()
    if s and s not in sents:
        sents.add(s)
        num_sent += 1

        f.write(u'{}\t{}\t{}\n'.format(sent_id, s, 'None'))
    return num_sent


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='the name of the FoLiA XML file that '
                        'should be processed.')
    parser.add_argument('output_dir', help='the directory where the '
                        'generated text files should be saved')
    args = parser.parse_args()

    file_name = args.file
    output_dir = args.output_dir

    act_tag = '{http://ilk.uvt.nl/folia}div'
    sentence_tag = '{http://ilk.uvt.nl/folia}s'
    note_tag = '{http://ilk.uvt.nl/folia}note'
    word_tag = '{http://ilk.uvt.nl/folia}w'
    t_tag = '{http://ilk.uvt.nl/folia}t'

    num_sent = 0
    num_emotional = 0
    sents = set()

    if os.path.basename(file_name).startswith('F'):
        fname = os.path.basename(file_name).replace('.xml.gz', '')
        fname = os.path.basename(fname).replace('.xml', '')
        out_file = os.path.join(output_dir, '{}.txt'.format(fname))
    else:
        out_file = os.path.join(output_dir, '{}.txt'.format(file_name[-20:-7]))
    print 'Writing file: {}'.format(out_file)

    # Load document
    if file_name.endswith('.gz'):
        fi = gzip.open(file_name)
    else:
        fi = file_name

    found_acts = False
    with codecs.open(out_file, 'wb', encoding='utf-8') as f:

        # First: try to find acts and extract sentences from the acts
        context = etree.iterparse(fi, events=('end',), tag=act_tag,
                                  huge_tree=True)
        try:
            for event, elem in context:
                #print elem.attrib
                if elem.get('class') == 'act':
                    if not found_acts:
                        print 'Extracting sentences from acts'
                    found_acts = True

                    # load div into memory
                    div_xml = BeautifulSoup(etree.tostring(elem), 'xml')
                    sentences = div_xml.find_all(sentence)
                    s = None
                    for sent in sentences:
                        if not note(sent.parent):
                            sent_id = sent.attrs.get('xml:id')

                            sent_words = [w.t.string
                                          for w in sent.find_all(word)]
                            num_sent = write_sentence(sent_id, sent_words,
                                                      sents, f, num_sent)
        except:
            pass
        del context

        if not found_acts:
            print 'Extracting sentences from s-tags'
            if file_name.endswith('.gz'):
                fi.close()
                fi = gzip.open(file_name)

            context = etree.iterparse(fi, events=('end',), tag=sentence_tag,
                                      huge_tree=True)

            for event, elem in context:
                if not elem.getparent().tag == note_tag:
                    sent_id = elem.get('{http://www.w3.org/XML/1998/namespace}id')
                    #print sent_id
                    sent_words = [w.find(t_tag).text
                                  for w in elem.findall(word_tag)]

                    num_sent = write_sentence(sent_id, sent_words, sents, f,
                                              num_sent)

    print '{} sentences\n'.format(num_sent)
