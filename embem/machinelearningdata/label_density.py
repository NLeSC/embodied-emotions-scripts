"""Calculate label density in HEEM data set.

Usage: python label_density.py <dir with train and test files>
"""
import codecs
from glob import glob
import numpy as np
import argparse
from collections import Counter

from embem.machinelearning.mlutils import load_data


def count_labelset_lengths(file_name):
    # load data set
    X_data, Y_data = load_data(file_name)

    Y = [set(s.split('_')) - {'None'} for s in Y_data]

    return [len(labelset) for labelset in Y]


parser = argparse.ArgumentParser()
parser.add_argument('input_dir', help='the directory where the input text '
                    'files can be found.')
args = parser.parse_args()

train_file = '{}/train_1.txt'.format(args.input_dir)
test_file = '{}/test_1.txt'.format(args.input_dir)

lengths_train = count_labelset_lengths(train_file)
lengths_test = count_labelset_lengths(test_file)

lengths = np.array(lengths_train+lengths_test)
print 'Label cardinality:', np.mean(lengths)
# divide by # labels => 42
print 'Label density:', np.mean((lengths/42.0))
