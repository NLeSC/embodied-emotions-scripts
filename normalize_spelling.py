"""Normalize the spelling of the data used for machine learning

Usage: python normalize_spelling <train set> <test set> <output dir>
"""

import codecs
import json
import argparse
from collections import Counter
import os
import string


with codecs.open('hist2modern_liwc.json', 'rb', 'utf-8') as f:
    full_dict = json.load(f, 'utf-8')

# create simple historic word -> modern word mapping
# (full_dict may contain multiple alternatives for a word)
hist2modern = {}
for w in full_dict.keys():
    if w not in full_dict[w]:
        c = Counter(full_dict[w])
        hist2modern[w] = c.most_common()[0][0]
print '#words in dict: {}'.format(len(hist2modern))

parser = argparse.ArgumentParser()
parser.add_argument('train', help='the name of the file containing the train '
                    'data.')
parser.add_argument('test', help='the name of the file containing the test '
                    'data.')
parser.add_argument('output_dir', help='the directory where the '
                    'generated text files should be saved')
args = parser.parse_args()

data_files = [args.train, args.test]

num_words = 0
num_replaced = 0
replacements = Counter()

for df in data_files:
    new_lines = []
    with codecs.open(df, 'rb', 'utf-8') as f:
        for line in f.readlines():
            l, label = line.rsplit(None, 1)
            words = l.split()
            result = []
            for word in words:
                w = word.lower()

                if w not in string.punctuation:
                    num_words += 1

                if w in hist2modern.keys():
                    result.append(hist2modern[w])
                    num_replaced += 1
                    replacements[w] += 1
                else:
                    result.append(word)
            new_lines.append('{}\t{}'.format(' '.join(result).encode('utf-8'),
                                             label))

    # write output
    _head, tail = os.path.split(df)
    out_file_name = '{}-normalized_spelling.txt'.format(tail.split('.')[0])
    out_file = os.path.join(args.output_dir, out_file_name)
    with codecs.open(out_file, 'wb', 'utf-8') as f:
        f.write('\n'.join(new_lines).decode('utf-8'))

# print number of replacements
print 'total words\t{}\ntotal replaced\t{}'.format(num_words, num_replaced)
for replaced, freq in replacements.most_common():
    print '{}\t{}\t{}'.format(replaced.encode('utf-8'),
                              hist2modern[replaced].encode('utf-8'),
                              freq)
