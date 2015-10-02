"""Script that calculates average F1 scores for all labels.

Usage: python calculate_average_f1.py <dir>
"""
import glob
import argparse
import codecs
import numpy as np


def read_data(input_dir):
    fname = '{}/output_*.txt'.format(input_dir)
    files = glob.glob(fname)

    results = {}

    for fi in files:
        with codecs.open(fi, 'rb', 'utf8') as f:
            for line in f.readlines():
                parts = line.split('\t')
                # Hamming score and F1's
                if len(parts) == 2:
                    l = parts[0]
                    n = float(parts[1].strip())
                    if not results.get(l):
                        results[l] = []
                    results[l].append(n)
                # meaures per label
                elif len(parts) == 5 and parts[0] != 'Label':
                    l = parts[0]
                    n = float(parts[4].strip())
                    if not results.get(l):
                        results[l] = []
                    results[l].append(n)
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='the name of the directory '
                        'containing machine learning results.')
    args = parser.parse_args()

    results = read_data(args.input_dir)

    for label, data in results.iteritems():
        print '{}\t{:.4f}\t{:.4f}'.format(label, np.mean(data), np.std(data))
