"""Script to train a rakel classifier.

Usage: python br_rakel.py <input dir> <output dir>
Made for use by do_rakel.sh: ./do_rakel.sh <data dir>

The script expects a train.txt and a test.txt containing the train and test
set in the data directory.
"""
from __future__ import print_function

import argparse

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.svm import LinearSVC

from rakel import RandomKLabelsets

from mlutils import get_data, print_results, split
from nltk.corpus import stopwords as sw
import string

import os

parser = argparse.ArgumentParser()
parser.add_argument('input_dir', help='directory containing the train and test'
                    ' data')
parser.add_argument('out_dir', help='directory output should be saved to')
args = parser.parse_args()

stopwords = sw.words('dutch') + [p for p in string.punctuation]

out_dir = args.out_dir
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

#classifier_dir = '{}/classifier/'.format(out_dir)
#if not os.path.exists(classifier_dir):
#    os.makedirs(classifier_dir)

for run in range(1, 11):
    print("Run", run)
    train_file = '{}/train_{}.txt'.format(args.input_dir, run)
    test_file = '{}/test_{}.txt'.format(args.input_dir, run)
    out_file = '{}/output_{}.txt'.format(out_dir, run)

    X_train, X_test, Y_train, Y_test, classes_ = get_data(train_file,
                                                          test_file)
    #print(Y_train.shape)

    clf = make_pipeline(TfidfVectorizer(analyzer=split,
                                        stop_words=stopwords),
                        RandomKLabelsets(LinearSVC(class_weight='auto'),
                                         n_estimators=Y_train.shape[1]*2,
                                         labels_per_estimator=3))
    clf.fit(X_train, Y_train)

    Y_pred = clf.predict(X_test)

    print_results(Y_test, Y_pred, classes_, open(out_file, 'w'))

# save classifier
#joblib.dump(clf, '{}/classifier.pkl'.format(classifier_dir))
