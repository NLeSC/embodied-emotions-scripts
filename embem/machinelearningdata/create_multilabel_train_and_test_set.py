"""Divide data in train (80%) and test set (20%) (10 folds)
The results are written to file. So this is done once.

Usage: python create_multiclass_train_and_test_set.py <dir with text files>
<output dir>
"""
from __future__ import print_function

import codecs
from glob import glob
import os
import numpy as np
import argparse
from scipy.linalg import norm

from sklearn.cross_validation import ShuffleSplit
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.cross_validation import KFold


def get_data(input_dir):
    for text_file in glob('{}/*.txt'.format(input_dir)):
        with codecs.open(text_file, 'r', 'utf-8') as f:
            for line in f.readlines():
                parts = line.rsplit('\t', 1)
                if len(parts) == 2:
                    yield parts[0], parts[1].strip()


def write_to_file(file_name, X, Y, indices):
    with codecs.open(file_name, 'wb', 'utf-8') as f:
        for x, y in zip(X[indices], Y[indices]):
            print(x, '\t',
                  '_'.join(mlb.inverse_transform(y.reshape(1, -1))[0]) or 'None',
                  file=f)


parser = argparse.ArgumentParser()
parser.add_argument('input_dir', help='the directory where the input text '
                    'files can be found.')
parser.add_argument('output_dir', help='the directory where the '
                    'generated text files should be saved')
args = parser.parse_args()

if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)

# load data
data = np.array(list(get_data(args.input_dir)))
np.random.shuffle(data)

sentences, labels = np.hsplit(data, 2)

# flatten the data
sentences = sentences.ravel()
labels = labels.ravel()

X = np.asarray(sentences, dtype=object)

Y = [set(s.split('_')) - {'None'} for s in labels]

mlb = MultiLabelBinarizer()
Y = mlb.fit_transform(Y)

print("Classes:\n", mlb.classes_)
print("Frequencies:\n", Y.sum(axis=0))
print("samples:\n", len(X))

count = 1
kf = KFold(len(X), n_folds=10)
for train_index, test_index in kf:
    write_to_file('{}/train_{}.txt'.format(args.output_dir, count), X, Y, train_index)
    write_to_file('{}/test_{}.txt'.format(args.output_dir, count), X, Y, test_index)
    print("Fold", count)
    print("Test frequencies:\n", Y[test_index].sum(axis=0))

    count += 1
