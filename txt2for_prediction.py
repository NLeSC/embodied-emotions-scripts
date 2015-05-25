"""Script to convert text file to input for embem classifier.

The script tokenizes the text and writes it to a new file containing:
<sentence id>\t<sentence (tokens separated by space)>\tNone\n

Usage: python txt2ml.py <dir in> <dir out>
"""

import argparse
import nltk.data
from nltk.tokenize import word_tokenize
import codecs
import os
from folia2dataset_for_prediction import write_sentence


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_in', help='directory containing the input text '
                        'files')
    parser.add_argument('dir_out', help='the name of the output directory')
    args = parser.parse_args()

    tokenizer = nltk.data.load('tokenizers/punkt/dutch.pickle')

    text_files = [t for t in os.listdir(args.dir_in) if t.endswith('.txt')]
    for text_file in text_files:
        print text_file,
        text = ''
        fname = os.path.join(args.dir_in, text_file)

        try:
            with codecs.open(fname, 'rb', 'utf8') as f:
                text = f.read()
        except:
            with codecs.open(fname, 'rb', 'latin-1') as f:
                text = f.read()

        # clean up text (remove strange html entities)
        text = text.replace('\n', ' ')
        text = text.replace(u"\u0092", "'")
        text = text.replace(u"\u0093", '"')
        text = text.replace(u"\u0097", "'")

        sentences = tokenizer.tokenize(text)

        sents = set()
        num_sent = 0
        fname = os.path.join(args.dir_out, text_file)
        with codecs.open(fname, 'wb', 'utf8') as f:
            for i, s in enumerate(sentences):
                words = word_tokenize(s)
                s_id = '{}_s_{}'.format(text_file.replace('.txt', ''), i)
                num_sent = write_sentence(s_id, words, sents, f, num_sent)
        print '{} sentences'.format(num_sent)
