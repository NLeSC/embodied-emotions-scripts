"""Script to train a binary relevance classifier.

Usage: python br_classifier.py <data dir> <seed> <run>
Made for use by experiment.sh: ./experiment.sh <data dir>

The script expects a train.txt and a test.txt containing the train and test
set in the data directory.
"""

from __future__ import print_function

from glob import glob
from itertools import chain
import argparse

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import accuracy_score, f1_score, hamming_loss, \
    precision_score, recall_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.svm import LinearSVC
from sklearn.externals import joblib
from nltk.corpus import stopwords as sw
import string
import os

from mlutils import get_data, print_results, split


class GridSearch(GridSearchCV):
    """Wrapper around GridSearchCV; workaround for scikit-learn issue #3484."""

    def decision_function(self, X):
        return super(GridSearch, self).decision_function(X)

    def predict(self, X):
        return super(GridSearch, self).predict(X)


parser = argparse.ArgumentParser()
parser.add_argument('input_dir', help='directory containing the train and test'
                    ' data')
parser.add_argument('out_dir', help='directory output should be saved to')
args = parser.parse_args()

stopwords = sw.words('dutch') + [p for p in string.punctuation]

out_dir = args.out_dir
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

for run in range(1, 11):
    print("Run", run)
    train_file = '{}/train_{}.txt'.format(args.input_dir, run)
    test_file = '{}/test_{}.txt'.format(args.input_dir, run)
    out_file = '{}/output_{}.txt'.format(out_dir, run)

    X_train, X_test, Y_train, Y_test, classes_ = get_data(train_file,
                                                          test_file)

    clf = make_pipeline(TfidfVectorizer(analyzer=split,
                                        stop_words=stopwords),
                        LinearSVC())

    clf = OneVsRestClassifier(clf, n_jobs=-1)

    clf.fit(X_train, Y_train)
    Y_pred = clf.predict(X_test)

    print_results(Y_test, Y_pred, classes_, open(out_file, 'w'))
