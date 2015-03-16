"""Find known body parts in sentences with predicted label 'Lichaamsdeel'.

Extended body parts are saved to new text files.

Usage: python classify_body_parts.py <json file with body part mapping> <dir
with input texts> <dir for output texts>
"""
import os
import codecs
import argparse
import json
import copy
from collections import Counter
from count_labels import load_data
from emotools.heem_utils import heem_body_part_labels, heem_emotion_labels
from count_labels import corpus_metadata
from genre2period import print_results_line_period

def get_emotion_body_part_pairs(file_name):
    # load data set
    X_data, Y_data = load_data(file_name)

    Y = [s.split('_') for s in Y_data]

    emotions2body = {}
    emotions = Counter()

    for labelset in Y:
        body_parts = [lb for lb in labelset if lb in heem_body_part_labels]
        emotion_lbls = [lb for lb in labelset if lb in heem_emotion_labels]

        if body_parts and emotion_lbls:
            for em in emotion_lbls:
                for bp in body_parts:
                    if not emotions2body.get(em):
                        emotions2body[em] = Counter()
                    emotions2body[em][bp] += 1
                    emotions[em] += 1
    return emotions, emotions2body


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='csv file containing corpus metadata')
    parser.add_argument('input_dir', help='the directory where the input text '
                        'files can be found.')
    args = parser.parse_args()

    f_name = args.file
    input_dir = args.input_dir

    text2period, text2year, text2genre, period2text, genre2text = \
        corpus_metadata(f_name)

    # statistics for entire corpus
    global_emotions = Counter()
    emotion_body_pairs = Counter()
    period_counters = {}

    # process texts
    text_files = [t for t in os.listdir(input_dir) if t.endswith('.txt')]
    for text_file in text_files:
        text_id = text_file.replace('.txt', '')
        in_file = os.path.join(input_dir, text_file)

        period = text2period.get(text_id)

        emotions, emotions2body = get_emotion_body_part_pairs(in_file)

        global_emotions.update(emotions)

        for em, body_counter in emotions2body.iteritems():
            if not period_counters.get(em):
                period_counters[em] = {}
            if not period_counters.get(em).get(period):
                period_counters[em][period] = Counter()
            period_counters[em][period].update(body_counter)

    for em, freq in global_emotions.most_common():
        print '{}\t{}'.format(em, freq)
        print 'Body part\tRenaissance\tClassisim\tEnlightenment\tNone\tTotal'

        merged_body_parts = Counter()
        for c in period_counters.get(em):
            merged_body_parts.update(period_counters.get(em).get(c))

        for label, freq in merged_body_parts.most_common():
            print print_results_line_period(label, period_counters.get(em))

        print
        print
