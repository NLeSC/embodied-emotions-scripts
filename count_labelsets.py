"""Create multilabel data set with normalized spelling.
The input consists of a directory of text files containing the dataset in
historic spelling.

The data set consists of:
<sentence id>\t<sentence>\tEmotie_Liefde (embodied emotions labels separated by
_)
<sentence id>\t<sentence>\tNone ('None' if no words were tagged)

Usage: python normalize_dataset.py <input dir> <output dir>
"""
import argparse
import codecs
import os
from collections import Counter


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='the name of the directory '
                        'containing text files that should be normalized.')
    args = parser.parse_args()

    input_dir = args.input_dir

    labelsets = Counter()
    len_labelset = Counter()

    print 'texts'
    text_files = [fi for fi in os.listdir(input_dir) if fi.endswith('.txt')]
    for text_file in text_files:
        print text_file

        in_file = os.path.join(input_dir, text_file)
        with codecs.open(in_file, 'rb', 'utf-8') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.split('\t')
                labels = parts[2].strip()
                labelsets[labels] += 1

                # count labelset lengths
                if labels != 'None':
                    length = len(labels.split('_'))
                    len_labelset[str(length).zfill(3)] += 1

    print '\n# different labelsets\t{}'.format(str(len(labelsets)))

    # print lengths
    print '\n# labels\tfrequency'
    for le, freq in len_labelset.most_common():
        print '{}\t{}'.format(le, freq)

    # print labelsets
    print '\nLabelset\tfrequency'
    for ls, freq in labelsets.most_common():
        print '{}\t{}'.format(ls, freq)
