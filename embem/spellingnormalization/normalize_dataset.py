"""Create multilabel data set with normalized spelling.
The input consists of a directory of text files containing the dataset in
historic spelling.

The data set consists of:
<sentence id>\t<sentence>\tEmotie_Liefde (embodied emotions labels separated by
_)
<sentence id>\t<sentence>\tNone ('None' if no words were tagged)

Usage: python normalize_dataset.py <input dir> <hist2modern dict> <output dir>
"""
import argparse
import codecs
import os
from collections import Counter
import json
import unicodedata
import string


def get_hist2modern(file_name):
    # load hist2modern dictionary
    with codecs.open(file_name, 'rb', 'utf-8') as f:
        full_dict = json.load(f, 'utf-8')

    # create simple historic word -> modern word mapping
    # (full_dict may contain multiple alternatives for a word)
    hist2modern = {}
    for w in full_dict.keys():
        if w not in full_dict[w]:
            c = Counter(full_dict[w])
            hist2modern[w] = c.most_common()[0][0]

    return hist2modern


def normalize_spelling(text, hist2modern, replacements):
    num_words = 0
    num_replaced = 0

    words = text.split(' ')

    new_words = []
    for w in words:
        if w not in string.punctuation:
            num_words += 1

        wo = w.lower()
        if wo in hist2modern.keys():
            new_words.append(hist2modern[wo])
            num_replaced += 1
            replacements[wo] += 1
        else:
            new_words.append(w)

    # replace accented characters by unaccented ones
    s = unicodedata.normalize('NFKD', ' '.join(new_words)) \
                   .encode('ascii', 'ignore')
    return s, num_words, num_replaced


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='the name of the directory '
                        'containing text files that should be normalized.')
    parser.add_argument('hist2modern', help='json file containing historic2'
                        'modern mapping (json object)')
    parser.add_argument('output_dir', help='the directory where the '
                        'normalized data files should be saved.')
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # load hist2modern dictionary
    hist2modern = get_hist2modern(args.hist2modern)
    print '#words in dict: {}'.format(len(hist2modern))

    replacements = Counter()
    num_words = 0
    num_replaced = 0

    text_files = [fi for fi in os.listdir(input_dir) if fi.endswith('.txt')]
    for text_file in text_files:
        print text_file

        in_file = os.path.join(input_dir, text_file)
        out_file = os.path.join(output_dir, text_file)
        with codecs.open(in_file, 'rb', 'utf-8') as f:
            lines = f.readlines()

        with codecs.open(out_file, 'wb', 'utf-8') as f:
            for line in lines:
                parts = line.split('\t')
                s, num_words, num_replaced = normalize_spelling(parts[1],
                                                                hist2modern,
                                                                replacements)

                f.write(u'{}\t{}\t{}'.format(parts[0], s, parts[2]))

    # print number of replacements
    print 'total words\t{}\ntotal replaced\t{}'.format(num_words, num_replaced)
    for replaced, freq in replacements.most_common():
        print '{}\t{}\t{}'.format(replaced.encode('utf-8'),
                                  hist2modern[replaced].encode('utf-8'),
                                  freq)
