"""Script to create a csv containing additional metadata about corpus texts.

Metadata added:
- # lines per text
- # of lines for which at least one heem label is predicted
- avg # of labels per sentence
- period (renaissance, classicism, enlightenment)

Input: corpus csv, directory containing text files
Output: csv containing <text_id>, <# lines>

Usage: python create_additional_metadata.py <corpus csv> <dir in> <file out>
"""
import argparse
import glob
import os
import pandas as pd
from genre2period import get_time_period
from embem.machinelearningdata.count_labels import load_data, count_lines, \
    num_emotional_sentences, average_number_of_labels


def get_tp(row):
    return get_time_period(row[1])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('corpus', help='file containing corpus metadata')
    parser.add_argument('in_dir', help='the directory containing the'
                        ' files with the correct labels.')
    parser.add_argument('out_file', help='csv file to write the output to')
    args = parser.parse_args()

    corpus = args.corpus
    in_dir = args.in_dir
    out_file = args.out_file

    data = {'#lines': [], '#emotional': [], 'avg_labels': []}
    index = []

    # get # of lines`
    text_files = glob.glob('{}/*.txt'.format(in_dir))
    for t in text_files:
        text_id = os.path.basename(t).replace('.txt', '')
        index.append(text_id)
        X_data, Y_data = load_data(t)
        data['#lines'].append(count_lines(t))
        data['#emotional'].append(num_emotional_sentences(Y_data))
        data['avg_labels'].append(average_number_of_labels(Y_data))
    df = pd.DataFrame(data=data, index=index)

    # get time period
    corpus = pd.read_csv(corpus, sep='\t', header=None, index_col=0)
    corpus.loc[:, 'period'] = corpus.apply(get_tp, axis=1)

    # write result to file
    result = pd.concat([df, corpus['period']], axis=1)
    result.to_csv(out_file)
