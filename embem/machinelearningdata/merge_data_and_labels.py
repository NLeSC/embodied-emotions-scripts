"""Merge sentences from one file to HEEM labels in another.
This script is used to combine predicted labels and unnormalized sentences to
make it easier to inspect/interpret label predictions for individual sentences.

Usage: python merge_data_and_labels.py <input_dir_labels> <input_dir_data>
<output dir>
"""
import os
import codecs
import argparse
import json
from embem.machinelearningdata.count_labels import load_data


def merge_data_and_labels(labels_file, data_file, out_file):
    # load data set
    X_labels, Y_labels = load_data(labels_file)
    X_data, Y_data = load_data(data_file)

    with codecs.open(out_file, 'wb', 'utf-8') as f:
        for i in range(len(X_data)):
            f.write(u'{}\t{}\n'.format(X_data[i].decode('utf-8'), Y_labels[i]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    #parser.add_argument('file', help='json file containing the body part '
    #                    'words mapping.')
    parser.add_argument('input_dir_labels', help='the directory containing the'
                        ' files with the correct labels.')
    parser.add_argument('input_dir_data', help='the directory containing the'
                        ' files with the correct sentences can be found.')
    parser.add_argument('output_dir', help='the directory where the output '
                        'files should be written.')
    args = parser.parse_args()

    #file_name = args.file
    input_dir_labels = args.input_dir_labels
    input_dir_data = args.input_dir_data
    output_dir = args.output_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    mapping = {}

    # read body part mapping
    #with codecs.open(file_name, 'rb', 'utf8') as f:
    #    mapping = json.load(f, encoding='utf8')

    # reverse body part mapping
    #word2cat = {}
    #for la, ws in mapping.iteritems():
    #    for word in ws:
    #        if not word2cat.get(word):
    #            word2cat[word] = la
    #        else:
    #            print 'ignored: {} ({})'.format(word, la)

    # process texts
    text_files = [t for t in os.listdir(input_dir_data) if t.endswith('.txt')]
    for i, text_file in enumerate(text_files):
        print '({} of {}) {}'.format((i+1), len(text_files), text_file)
        labels_file = os.path.join(input_dir_labels, text_file)
        data_file = os.path.join(input_dir_data, text_file)
        out_file = os.path.join(output_dir, text_file)

        merge_data_and_labels(labels_file, data_file, out_file)
