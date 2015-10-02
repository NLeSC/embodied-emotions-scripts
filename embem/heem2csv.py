"""Count the numbers of words annotated with heem entities in the corpus that
was manually annotated.

Data used in paper 2.

Usage: python heem2csv.py <dir containing the folia files with
EmbodiedEmotions annotations> <csv file out>
"""
from lxml import etree
from embem.emotools.bs4_helpers import sentence, note
import argparse
import os
from collections import Counter
from embem.emotools.heem_utils import heem_concept_type_labels, \
    heem_emotion_labels
import pandas as pd


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_name', help='the name of the dir containing the '
                        'FoLiA XML files that should be processed.')
    parser.add_argument('file_out', help='name of the json file where the '
                        'statistics should be stored.')
    args = parser.parse_args()

    dir_name = args.dir_name

    entity_class = u'EmbodiedEmotions'

    entity_tag = '{http://ilk.uvt.nl/folia}entity'

    os.chdir(dir_name)

    folia_counter = 0
    num_sent = 0
    num_emotional = 0
    stats = Counter()
    entity_words = {}
    text_stats = {}

    heem_labels = heem_concept_type_labels + heem_emotion_labels
    result = pd.DataFrame(columns=heem_labels)

    for i, f in enumerate(os.listdir(dir_name)):
        print '{} ({} of {})'.format(f, i+1, len(os.listdir(dir_name)))

        text_id = f[0:13]
        heem_stats = Counter()

        sents = set()
        # load document
        context = etree.iterparse(f, events=('end',), tag=entity_tag,
                                  huge_tree=True)
        for event, elem in context:
            ent_class = elem.attrib.get('class')
            embem_parts = ent_class.split(':')
            if len(embem_parts) > 1:
                l = embem_parts[1]
                if l in heem_labels:
                    wrefs = elem.findall('{http://ilk.uvt.nl/folia}wref')
                    heem_stats[l] += len(wrefs)

        del context
        result.loc[text_id] = pd.Series(heem_stats)
    result = result.fillna(0)
    print result
    result.to_csv(args.file_out)
