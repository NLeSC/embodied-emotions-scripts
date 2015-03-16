"""Count HEEM labels in data set.

Usage: python count_labels.py <dir with train and test files>
"""
import os
import codecs
import argparse
from collections import Counter
from genre2period import get_time_period
from emotools.heem_utils import heem_concept_type_labels, heem_emotion_labels


def load_data(data_file):
    data = [ln.rsplit(None, 1) for ln in open(data_file)]

    X_data, Y_data = zip(*data)

    return X_data, Y_data


def count_labels(file_name):
    counter = Counter()
    # load data set
    X_data, Y_data = load_data(file_name)

    Y = [s.split('_') for s in Y_data]

    for labelset in Y:
        counter.update(labelset)

    del counter['None']

    return counter


def count_lines(file_name):
    with open(file_name) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def corpus_metadata(file_name):
    text2genre = {}
    text2year = {}
    text2period = {}
    genre2text = {}
    period2text = {}

    # read text metadata
    with codecs.open(file_name, 'rb', 'utf8') as f:
        for line in f.readlines():
            parts = line.split('\t')
            text_id = parts[0]
            period = get_time_period(parts[1])
            genre = parts[2]
            year = parts[1]

            text2genre[text_id] = genre
            text2year[text_id] = year
            text2period[text_id] = period

            if genre not in genre2text.keys():
                genre2text[genre] = []
            genre2text[genre].append(text_id)

            if period not in period2text.keys():
                period2text[period] = []
            period2text[period].append(text_id)

    return text2period, text2year, text2genre, period2text, genre2text

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='the name of the FoLiA XML file that '
                        'should be processed.')
    parser.add_argument('input_dir', help='the directory where the input text '
                        'files can be found.')
    args = parser.parse_args()

    file_name = args.file

    text2period, text2year, text2genre, period2text, genre2text = \
        corpus_metadata(file_name)

    text2labels = {}
    text2lines = {}

    # process texts
    input_dir = args.input_dir
    text_files = [t for t in os.listdir(input_dir) if t.endswith('.txt')]
    for text_file in text_files:
        in_file = os.path.join(input_dir, text_file)
        text_id = text_file.replace('.txt', '')
        text2labels[text_id] = count_labels(in_file)
        text2lines[text_id] = count_lines(in_file)

    # to normalize results
    r_l = [text2lines[t_id] for t_id in period2text.get('renaissance', [])]
    c_l = [text2lines[t_id] for t_id in period2text.get('classisism', [])]
    e_l = [text2lines[t_id] for t_id in period2text.get('enlightenment', [])]
    n_l = [text2lines[t_id] for t_id in period2text.get(None, [])]

    print '\tRenaissance\tClassisism\tEnlightenment\tNone'
    print '# texts\t{}\t{}\t{}\t{}'.format(len(period2text.get('renaissance', [])),
                                           len(period2text.get('classisism', [])),
                                           len(period2text.get('enlightenment', [])),
                                           len(period2text.get(None, [])))
    print '# lines\t{}\t{}\t{}\t{}'.format(sum(r_l), sum(c_l), sum(e_l), sum(n_l))

    print
    print

    # print labels per period
    labels = heem_concept_type_labels + heem_emotion_labels
    print 'Label\tRenaissance\tClassisism\tEnlightenment\tNone'
    for label in labels:
        r = [text2labels[t_id][label] for t_id in period2text.get('renaissance', [])]
        c = [text2labels[t_id][label] for t_id in period2text.get('classisism', [])]
        e = [text2labels[t_id][label] for t_id in period2text.get('enlightenment', [])]
        n = [text2labels[t_id][label] for t_id in period2text.get(None, [])]
        print '{}\t{}\t{}\t{}\t{}'.format(label, sum(r), sum(c), sum(e), sum(n))

