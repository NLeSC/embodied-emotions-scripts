"""Script that calculates statistical significance between two experiments.

Usage: python calculate_significance.py <dir 1> <dir 2>
"""

import argparse
from scipy.stats import ttest_ind
import numpy as np
from calculate_average_f1 import read_data

_label_mapping = {
    'Anger': 'Woede',
    'Sadness': 'Verdriet',
    'Love': 'Liefde',
    'Fear': 'Angst',
    'Joy': 'Blijdschap',
    'Desire': 'Verlangen',
    'Despair': 'Wanhoop',
    'Disgust': 'Walging',
    'PosSentiments': 'Ontroering',
    'Compassion': 'Mededogen',
    'PrideHonour': 'Eergevoel',
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir1', help='the name of the directory '
                        'containing text files that should be normalized.')
    parser.add_argument('input_dir2', help='the name of the directory '
                        'containing text files that should be normalized.')
    args = parser.parse_args()

    results1 = read_data(args.input_dir1)
    results2 = read_data(args.input_dir2)

    exp_name1 = args.input_dir1.replace('/home/jvdzwaan/data/ml/', '')
    exp_name2 = args.input_dir2.replace('/home/jvdzwaan/data/ml/', '')

    print 'Label\t{} avg\t{} std\t{} avg\t{} std\tp'.format(exp_name1,
                                                            exp_name1,
                                                            exp_name2,
                                                            exp_name2)

    labels_for_all = ['Hamming score (acc)', 'F1 (micro-averaged)',
                      'F1 (macro-averaged)', 'Emotie', 'Lichaamswerking',
                      'Lichaamsdeel', 'EmotioneleHandeling']
    other_labels = [l for l in results1.keys() if l not in labels_for_all]
    other_labels.sort()

    for label in labels_for_all + other_labels:
        if label not in results2.keys():
            label2 = _label_mapping.get(label)
        else:
            label2 = label

        d1 = results1.get(label)
        d2 = results2.get(label2)
        t, prob = ttest_ind(d1, d2, equal_var=False)
        print '{}\t{:.4f}\t{:.4f}\t{:.4f}\t{:.4f}\t{:.4f}'.format(label,
                                                                  np.mean(d1),
                                                                  np.std(d1),
                                                                  np.mean(d2),
                                                                  np.std(d2),
                                                                  prob)
