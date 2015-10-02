"""Translate Dutch HEEM labels to English.

Usage: python translate_labels.py <dir with input texts> <dir for output texts>
"""
import os
import codecs
import argparse
import json
import pandas as pd

from embem.machinelearningdata.count_labels import load_data
from embem.emotools.heem_utils import heem_labels_en

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='the directory where the input text '
                        'files can be found.')
    parser.add_argument('output_dir', help='the directory where the output '
                        'files should be written.')
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    text_files = [t for t in os.listdir(input_dir) if t.endswith('.txt')]
    for text_file in text_files:
        in_file = os.path.join(input_dir, text_file)
        x_data, y_data = load_data(in_file)
        labels = [y.split('_') for y in y_data]
        #new_labels = []
        out_file = os.path.join(output_dir, text_file)
        #print out_file
        with codecs.open(out_file, 'wb', 'utf-8') as f:
            for i in range(len(labels)):
                ls = labels[i]
                #new_labels.append([heem_labels_en.get(l, 'None') for l in ls])
                new_labels = [heem_labels_en.get(l, 'None') for l in ls]
                #print ls, new_labels
                f.write(u'{}\t{}\n'.format(x_data[i].decode('utf-8'),
                                           '_'.join(new_labels)))
