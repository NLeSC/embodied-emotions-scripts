"""Script to write csv file with label counts for each text.

Usage: python count_labels.py <dir containing predicted labels> <out_file>
"""
import argparse
import glob
import os
from embem.emotools.heem_utils import heem_concept_type_labels, \
    heem_emotion_labels, heem_body_part_labels
import pandas as pd
from collections import Counter
import codecs
from embem.corpus.genre2period import get_time_period
import numpy as np


def load_data(data_file):
    data = [ln.rsplit(None, 1) for ln in open(data_file)]

    X_data, Y_data = zip(*data)

    return X_data, Y_data


def count_labels(file_name):
    counter = Counter()
    # load data set
    X_data, Y_data = load_data(file_name)

    Y = [s.split('_') for s in Y_data]

    for labelset in Y:
        counter.update(labelset)

    del counter['None']

    return counter


def count_lines(file_name):
    with open(file_name) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def num_emotional_sentences(Y_data):
    em = [p for p in Y_data if not p == 'None']
    return len(em)


def average_number_of_labels(Y_data):
    lengths = [len(ls.split('_')) if not ls == 'None' else 0 for ls in Y_data]
    return np.mean(lengths)


def corpus_metadata(file_name):
    text2genre = {}
    text2year = {}
    text2period = {}
    genre2text = {}
    period2text = {}

    # read text metadata
    with codecs.open(file_name, 'rb', 'utf8') as f:
        for line in f.readlines():
            parts = line.split('\t')
            text_id = parts[0]
            period = get_time_period(parts[1])
            genre = parts[2]
            year = parts[1]

            text2genre[text_id] = genre
            text2year[text_id] = year
            text2period[text_id] = period

            if genre not in genre2text.keys():
                genre2text[genre] = []
            genre2text[genre].append(text_id)

            if period not in period2text.keys():
                period2text[period] = []
            period2text[period].append(text_id)

    return text2period, text2year, text2genre, period2text, genre2text

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='the directory where the input text '
                        'files can be found.')
    parser.add_argument('out_file', help='name of the output file')
    args = parser.parse_args()

    files = glob.glob('{}/*.txt'.format(args.input_dir))

    labels = heem_concept_type_labels + heem_emotion_labels + \
        heem_body_part_labels
    index = [os.path.basename(f).replace('.txt', '') for f in files]

    df = pd.DataFrame(columns=labels, index=index)

    for f in files:
        text_id = os.path.basename(f).replace('.txt', '')
        #print text_id
        label_counts = count_labels(f)
        df.loc[text_id] = pd.Series(label_counts)
    df = df.fillna(0)
    df.to_csv(args.out_file)
