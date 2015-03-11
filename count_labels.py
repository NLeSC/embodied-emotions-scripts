"""Count HEEM labels in data set.

Usage: python count_labels.py <dir with train and test files>
"""
import codecs
from glob import glob
import numpy as np
import argparse
from collections import Counter


def load_data(data_file):
    data = [ln.rsplit(None, 1) for ln in open(data_file)]

    X_data, Y_data = zip(*data)

    return X_data, Y_data


def count_labels(file_name, counter):
    # load data set
    X_data, Y_data = load_data(file_name)

    Y = [s.split('_') for s in Y_data]

    for labelset in Y:
        counter.update(labelset)

    del counter['None']

    return counter


parser = argparse.ArgumentParser()
parser.add_argument('input_dir', help='the directory where the input text '
                    'files can be found.')
args = parser.parse_args()

train_file = '{}/train_1.txt'.format(args.input_dir)
test_file = '{}/test_1.txt'.format(args.input_dir)

labels = Counter()
labels = count_labels(train_file, labels)
labels = count_labels(test_file, labels)

for l, freq in labels.most_common():
    print '{}\t{}'.format(l, freq)

