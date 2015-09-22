"""Class to create RAKEL classifier
"""
from itertools import combinations
from math import factorial

import numpy as np

from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.utils.random import check_random_state, choice


def _binomial(n, k):
    return factorial(n) // (factorial(k) * factorial(n - k))


def _fit_base_estimator(estimator, X, Y, labels_per_estimator,
                        labelset):
                        #random_state):
    #labelset = choice(np.arange(Y.shape[1]), labels_per_estimator,
                      #replace=False, random_state=random_state)
    y = [''.join(map(repr, row)) for row in Y[:, labelset]]
    #y = map(repr, Y[:, labelset])
    return labelset, clone(estimator).fit(X, y)


class RandomKLabelsets(BaseEstimator, ClassifierMixin):
    """Random k-labelsets multi-label ensemble classifier."""

    def __init__(self, base_estimator, n_estimators=10,
                 labels_per_estimator=2, random_state=None):
        #super(RandomKLabelsets, self).__init__(base_estimator, n_estimators)
        self.base_estimator = base_estimator
        self.n_estimators = n_estimators
        self.labels_per_estimator = labels_per_estimator
        self.random_state = random_state

    def fit(self, X, Y):
        random_state = check_random_state(self.random_state)
        all_label_sets = [c for c in combinations(range(Y.shape[1]), 3)]
        random_label_sets = [all_label_sets[i] for i in np.random.choice(range(len(all_label_sets)),
                                             self.n_estimators,
                                             replace=False)]
        #print('aantal random labelsets', len(random_label_sets))
        estimators = [_fit_base_estimator(self.base_estimator, X, Y,
                                          self.labels_per_estimator,
                                          c)
                      for c in random_label_sets]

        self.estimators_ = estimators
        self.n_labels_ = Y.shape[1]

        return self

    def predict(self, X):
        return self.predict_proba(X) > .5

    def predict_proba(self, X):
        n_samples = X.shape[0]
        sums = np.zeros((n_samples, self.n_labels_))
        votes = np.zeros((n_samples, self.n_labels_))

        for labelset, clf in self.estimators_:
            y = np.asarray([map(int, row) for row in clf.predict(X)],
                           dtype=bool)
            sums[:, labelset] += y
            votes[:, labelset] += 1

        return sums / votes
