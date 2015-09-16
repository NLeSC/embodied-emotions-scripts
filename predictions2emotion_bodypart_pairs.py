"""Generate visualization pairs (emotion label - body part) for predicted
labels.

Input: directory containing text files with predicted heem labels and expanded
body parts.

Generates a csv file containing the text id in the first column and a column
containing frequencies for each found emotion-body part pair.

Usage: python predictions2emotion_bodypart_pairs.py <dir in> <dir out>
"""
import argparse
import glob
import os
from count_labels import load_data
from emotools.heem_utils import heem_emotion_labels, heem_body_part_labels
from collections import Counter
import pandas as pd


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='directory containing files with '
                        'predictions.')
    parser.add_argument('output_file', help='name of the csv file to save the '
                        'data to')
    args = parser.parse_args()

    input_dir = args.input_dir
    output_file = args.output_file

    all_pairs = set()
    texts = []
    data = {}
    embodied = {}

    text_files = glob.glob(os.path.join(input_dir, '*.txt'))
    for i, text_file in enumerate(text_files):
        print '({} of {}) {}'.format((i+1), len(text_files), text_file)
        text_id = os.path.basename(text_file).replace('.txt', '')
        texts.append(text_id)

        data[text_id] = Counter()
        embodied[text_id] = Counter()

        X_data, Y_data = load_data(text_file)

        for j, predicted in enumerate(Y_data):
            lbs = (set(predicted.split('_')) - {'None'})
            emotion_labels = [l for l in lbs if l in heem_emotion_labels]
            ct_labels = [l for l in lbs if l in heem_body_part_labels]
            if emotion_labels and ct_labels:
                for e in emotion_labels:
                    for ct in ct_labels:
                        pair = '{}_{}'.format(e, ct)
                        all_pairs.add(pair)
                        data[text_id][pair] += 1
                    embodied[text_id]['Embodied_{}'.format(e)] += 1

    # write to file
    all_pairs = list(all_pairs)
    all_pairs.sort()

    embodied_labels = ['Embodied_{}'.format(l) for l in heem_emotion_labels]

    df = pd.DataFrame(columns=all_pairs+embodied_labels, index=texts)
    for text_id, counter in data.iteritems():
        df.loc[text_id] = pd.Series(counter + embodied[text_id])
    df.fillna(0).to_csv(output_file)
