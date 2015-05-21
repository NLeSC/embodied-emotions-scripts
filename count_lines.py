"""Script to count the lines in a corpus of texts.

This information can be used to normalize the results.

Input: directory containing text files
Output: csv containing <text_id>, <# lines>

Usage: python count_lines.py <dir in> <file out>
"""
import argparse
import glob
import os
import codecs
import pandas as pd


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_dir', help='the directory containing the'
                        ' files with the correct labels.')
    parser.add_argument('out_file', help='the directory where the output '
                        'files should be written.')
    args = parser.parse_args()

    in_dir = args.in_dir
    out_file = args.out_file

    data = {'#lines': []}
    index = []

    text_files = glob.glob('{}/*.txt'.format(in_dir))
    for t in text_files:
        text_id = os.path.basename(t).replace('.txt', '')
        with codecs.open(t, 'rb', 'utf8') as f:
            data['#lines'].append(len(f.readlines()))
            index.append(text_id)
    df = pd.DataFrame(data=data, index=index)
    df.to_csv(out_file)
