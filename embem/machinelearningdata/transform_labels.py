"""Transform HEEM labels in text files

Usage: python transform_labels.py <dir in> <dir out> --replacements
<replacements file>
"""
from __future__ import print_function

import codecs
import os
import argparse
import json


def transform_labels(labels_str, replacements):
    labels = labels_str.strip().split('_')

    # remove unwanted labels
    #unwanted = ['Emotie', 'EmotioneleHandeling', 'Lichaamsdeel',
    #            'Lichaamswerking']
    #labels = [l for l in labels if l not in unwanted]

    # replace labels
    for r, ls in replacements.iteritems():
        for l in ls:
            if l in labels:
                labels.remove(l)
                labels.append(r)
    labels = list(set(labels))
    labels.sort()

    # no labels left in label set
    if not labels:
        labels.append('None')

    return '_'.join(labels)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='the name of the directory '
                        'containing text files that should be normalized.')
    parser.add_argument('output_dir', help='the directory where the '
                        'normalized data files should be saved.')
    parser.add_argument('--replacements', help='the name of the json object '
                        'containing label replacements.')
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    replacements = {}

    if args.replacements:
        with codecs.open(args.replacements, 'rb', encoding='utf8') as f:
            replacements = json.load(f)

    text_files = [fi for fi in os.listdir(input_dir) if fi.endswith('.txt')]
    for text_file in text_files:
        print(text_file)

        in_file = os.path.join(input_dir, text_file)
        out_file = os.path.join(output_dir, text_file)

        with codecs.open(in_file, 'rb', 'utf-8') as f:
            lines = f.readlines()

        with codecs.open(out_file, 'wb', 'utf-8') as f:
            for line in lines:
                parts = line.rsplit('\t', 1)
                labels = transform_labels(parts[1], replacements)

                print(parts[0]+'\t'+labels, file=f)
