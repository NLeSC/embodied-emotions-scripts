from __future__ import print_function

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


def load_data(data_file):
    data = [ln.rsplit(None, 1) for ln in open(data_file)]

    X_data, Y_data = zip(*data)

    return X_data, Y_data


def get_data(train_file, test_file):
    X_train, Y_train = load_data(train_file)
    X_train = [ln.split('\t')[1] for ln in X_train]
    X_test, Y_test = load_data(test_file)
    X_test = [ln.split('\t')[1] for ln in X_test]

    mlb = MultiLabelBinarizer()
    Y_train = [set(s.split('_')) - {'None'} for s in Y_train]
    Y_test = [set(s.split('_')) - {'None'} for s in Y_test]
    Y_train = mlb.fit_transform(Y_train)
    Y_test = mlb.transform(Y_test)

    return X_train, X_test, Y_train, Y_test, mlb.classes_


def print_results(Y_test, Y_pred, classes_, f):
    print("Hamming score (acc)\t", 1 - hamming_loss(Y_test, Y_pred), file=f)
    print("F1 (micro-averaged)\t", f1_score(Y_test, Y_pred, average='micro'), file=f)
    print("F1 (macro-averaged)\t", f1_score(Y_test, Y_pred, average='macro'), file=f)
    print("\nLabel\tAccuracy\tPrecision\tRecall\tF1", file=f)
    for i, label in enumerate(classes_):
        print(label + "\t" +
            "%.4f" % accuracy_score(Y_test[:, i], Y_pred[:, i]) + "\t" +
            "%.4f" % precision_score(Y_test[:, i], Y_pred[:, i]) + "\t" +
            "%.4f" % recall_score(Y_test[:, i], Y_pred[:, i]) + "\t" +
            "%.4f" % f1_score(Y_test[:, i], Y_pred[:, i]), file=f)


def split(s):
    return s.split()
