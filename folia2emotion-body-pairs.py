"""Create data set for visualization assignment
The data set consists of:
<sentence id>\t<emotion label>\t<other label>\t<tagged words>

Usage: python folia2visualization-pairs.py <file in> <output dir>
Or: ./batch_do_python.sh folia2visualization-pairs.py <dir in> <output dir>
(for a directory containing folia files)
"""
from lxml import etree
from bs4 import BeautifulSoup
from emotools.bs4_helpers import sentence, note
import argparse
import codecs
import os
from itertools import product
from collections import Counter
import json


def get_time_period(year):
    year = int(year)
    if year >= 1600 and year < 1660:
        return 'renaissance'
    elif year >= 1660 and year < 1750:
        return 'classisism'
    elif year >= 1750 and year <= 1800:
        return 'enlightenment'
    else:
        return None


def read_statistics(file_name):
    stats = {}
    label_count = Counter()
    current_label = None

    with codecs.open(file_name, 'rb', 'utf8') as f:
        for line in f.readlines():
            parts = line.split('\t')
            if len(parts) == 2:
                current_label = parts[0]
                label_count[current_label] = int(parts[1])
                stats[current_label] = Counter()
            elif len(parts) == 3:
                stats[current_label][parts[0]] = int(parts[2])
    return stats, label_count


def get_hist2modern():
    # load hist2modern dictionary
    with codecs.open('hist2modern_bwnt.json', 'rb', 'utf-8') as f:
        full_dict = json.load(f, 'utf-8')

    # create simple historic word -> modern word mapping
    # (full_dict may contain multiple alternatives for a word)
    hist2modern = {}
    for w in full_dict.keys():
        if w not in full_dict[w]:
            c = Counter(full_dict[w])
            hist2modern[w] = c.most_common()[0][0]
    return hist2modern


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='the name of the FoLiA XML file that '
                        'should be processed.')
    parser.add_argument('output_dir', help='the directory where the '
                        'generated text files should be saved')
    args = parser.parse_args()

    file_name = args.file
    output_dir = args.output_dir

    text_id = file_name[-20:-7]

    # read text metadata
    period = None
    with codecs.open('annotation_corpus_metadata.csv', 'rb', 'utf8') as f:
        for line in f.readlines():
            parts = line.split('\t')
            if parts[0] == text_id:
                period = get_time_period(parts[1])

    act_tag = '{http://ilk.uvt.nl/folia}div'

    # Load document
    context = etree.iterparse(file_name, events=('end',), tag=act_tag)

    if period:
        out_file = os.path.join(output_dir, '{}.txt'.format(period))
        if not os.path.exists(out_file):
            stats = {}
            label_count = Counter()
        else:
            stats, label_count = read_statistics(out_file)

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
                        bodyLabels = []

                        for entity in sent.find_all('entity'):
                            e = entity.attrs.get('class')

                            # get emotion labels
                            if e.startswith('EmbodiedEmotions-EmotionLabel'):
                                emotionLabels.append(entity)

                            # get body labels
                            if e.endswith('Lichaamsdeel'):
                                bodyLabels.append(entity)

                        if len(emotionLabels) > 0 and len(bodyLabels) > 0:
                            p = product(emotionLabels, bodyLabels)
                            for c in p:
                                ent1 = c[0]
                                label1 = ent1.attrs.get('class').split(':')[1]
                                words1 = [w.attrs.get('t')
                                          for w in ent1.find_all('wref')]
                                ent2 = c[1]
                                #label2 = ent2.attrs.get('class').split(':')[1]
                                words2 = [w.attrs.get('t')
                                          for w in c[1].find_all('wref')]
                                if set(words1).issubset(words2) or set(words2).issubset(words1):
                                    if len(words1) < len(words2):
                                        ent_words = ' '.join(words1).lower()
                                    else:
                                        ent_words = ' '.join(words2).lower()
                                    if not stats.get(label1):
                                        stats[label1] = Counter()
                                    stats[label1][ent_words] += 1
                                    label_count[label1] += 1

        hist2modern = get_hist2modern()

        print 'Writing to {}'.format(out_file)
        with codecs.open(out_file, 'wb', encoding='utf-8') as f:
            for label, lfreq in label_count.most_common():
                f.write(u'{}\t{}\n'.format(label, lfreq))
                for word, freq in stats[label].most_common():
                    modern_w = hist2modern.get(word, word)
                    f.write(u'{}\t{}\t{}\n'.format(word, modern_w, freq))
                f.write('\n')
        print
