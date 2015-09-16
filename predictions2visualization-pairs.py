"""Generate visualization pairs (emotion label - concept type) for predicted
labels.

Input: directory containing text files with predicted heem labels.

Generates a text file containing
<text_id>\t<sentence id>\t<emotion label>\t<concept type label>
for each file in the input dir.

Usage: python predictions2visualization.py <dir in> <dir out>
"""
import argparse
import glob
import os
import codecs
from count_labels import load_data
from emotools.heem_utils import heem_emotion_labels, heem_concept_type_labels
from collections import Counter


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='directory containing files with '
                        'predictions.')
    parser.add_argument('output_dir', help='the directory where the '
                        'generated text files should be saved')
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    pairs = Counter()

    text_files = glob.glob(os.path.join(input_dir, '*.txt'))
    for i, text_file in enumerate(text_files):
        print '({} of {}) {}'.format((i+1), len(text_files), text_file)
        text_id = text_file[-17:-4]

        X_data, Y_data = load_data(text_file)

        out_file = os.path.join(output_dir, os.path.basename(text_file))
        for j, predicted in enumerate(Y_data):
            lbs = (set(predicted.split('_')) - {'None'})
            emotion_labels = [l for l in lbs if l in heem_emotion_labels]
            ct_labels = [l for l in lbs if l in heem_concept_type_labels]
            if emotion_labels and ct_labels:
                for e in emotion_labels:
                    for ct in ct_labels:
                        pairs['{}\t{}'.format(e, ct)] += 1

        with codecs.open(out_file, 'wb', 'utf-8') as f:
            for pair, freq in pairs.most_common():
                f.write('{}\t{}\t{}\n'.format(text_id, pair, freq))
