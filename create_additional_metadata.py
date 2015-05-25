"""Script to create a csv containing additional metadata about corpus texts.

Metadata added:
- # lines per text
- period (renaissance, classicism, enlightenment)

Input: corpus csv, directory containing text files
Output: csv containing <text_id>, <# lines>

Usage: python count_lines.py <corpus csv> <dir in> <file out>
"""
import argparse
import glob
import os
import codecs
import pandas as pd
from genre2period import get_time_period


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

    data = {'#lines': []}
    index = []

    # get # of lines`
    text_files = glob.glob('{}/*.txt'.format(in_dir))
    for t in text_files:
        text_id = os.path.basename(t).replace('.txt', '')
        with codecs.open(t, 'rb', 'utf8') as f:
            data['#lines'].append(len(f.readlines()))
            index.append(text_id)
    df = pd.DataFrame(data=data, index=index)

    # get time period
    corpus = pd.read_csv(corpus, sep='\t', header=None, index_col=0)
    corpus.loc[:, 'period'] = corpus.apply(get_tp, axis=1)

    # write result to file
    result = pd.concat([df, corpus['period']], axis=1)
    result.to_csv(out_file)
