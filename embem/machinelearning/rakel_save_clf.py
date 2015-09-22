"""Script to train rakel classifier (based on all data) and save classifier
object

The classifier object is saved to <output_dir>/classifier.pkl

Usage: python rakel_save_clf.py <train file> <output_dir>
"""
from __future__ import print_function

import argparse

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.svm import LinearSVC
from sklearn.externals import joblib

from rakel import RandomKLabelsets

from mlutils import get_data, split
from nltk.corpus import stopwords as sw
import string

import os

parser = argparse.ArgumentParser()
parser.add_argument('train_file', help='file containing the train data')
parser.add_argument('output_dir', help='directory to save the classifier to')
args = parser.parse_args()

stopwords = sw.words('dutch') + [p for p in string.punctuation]

if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)

classifier_file = '{}/classifier.pkl'.format(args.output_dir)

X_train, X_test, Y_train, Y_test, classes_ = get_data(args.train_file,
                                                      args.train_file)

clf = make_pipeline(TfidfVectorizer(analyzer=split,
                                    stop_words=stopwords),
                    RandomKLabelsets(LinearSVC(class_weight='auto'),
                                     n_estimators=Y_train.shape[1]*2,
                                     labels_per_estimator=3))
clf.fit(X_train, Y_train)

# save classifier
joblib.dump(clf, classifier_file)
