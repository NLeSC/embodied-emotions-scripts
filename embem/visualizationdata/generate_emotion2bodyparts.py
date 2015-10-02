"""Create csv files with emotions in the first column and a column for every
expanded body part.

Usage: python generate_emotion2bodyparts.py <corpus metadata> <dir
with input texts> <output file (.csv)>

In addition to the output.csv, also files for each time period are written.
"""
import os
import argparse
from collections import Counter
from embem.machinelearningdata.count_labels import load_data, corpus_metadata
from embem.emotools.heem_utils import heem_body_part_labels, \
    heem_emotion_labels
import pandas as pd


def get_emotion_body_part_pairs(file_name):
    # load data set
    X_data, Y_data = load_data(file_name)

    Y = [s.split('_') for s in Y_data]

    emotions2body = {}
    emotions = Counter()

    for labelset in Y:
        body_parts = [lb for lb in labelset if lb in heem_body_part_labels]
        emotion_lbls = [lb for lb in labelset if lb in heem_emotion_labels]

        if body_parts and emotion_lbls:
            for em in emotion_lbls:
                for bp in body_parts:
                    if not emotions2body.get(em):
                        emotions2body[em] = Counter()
                    emotions2body[em][bp] += 1
                    emotions[em] += 1
    return emotions, emotions2body


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_file', help='csv file containing corpus metadata')
    parser.add_argument('input_dir', help='the directory where the input text '
                        'files can be found.')
    parser.add_argument('out_file', help='csv file containing corpus metadata')
    args = parser.parse_args()

    f_name = args.in_file
    input_dir = args.input_dir
    out_file = args.out_file

    text2period, text2year, text2genre, period2text, genre2text = \
        corpus_metadata(f_name)

    # statistics for entire corpus
    global_emotions = Counter()
    emotion_body_pairs = Counter()
    period_counters = {}
    periods = set()

    # process texts
    text_files = [t for t in os.listdir(input_dir) if t.endswith('.txt')]
    for text_file in text_files:
        text_id = text_file.replace('.txt', '')
        in_file = os.path.join(input_dir, text_file)

        period = text2period.get(text_id)
        periods.add(period)

        emotions, emotions2body = get_emotion_body_part_pairs(in_file)

        global_emotions.update(emotions)

        for em, body_counter in emotions2body.iteritems():
            if not emotion_body_pairs.get(em):
                emotion_body_pairs[em] = Counter()
            emotion_body_pairs[em].update(body_counter)
            if not period_counters.get(em):
                period_counters[em] = {}
            if not period_counters.get(em).get(period):
                period_counters[em][period] = Counter()
            period_counters[em][period].update(body_counter)

    df = pd.DataFrame(columns=heem_body_part_labels, index=heem_emotion_labels)
    for em, body_counter in emotion_body_pairs.iteritems():
        df.loc[em] = pd.Series(body_counter)
        #print em
        #print body_counter
    df = df.fillna(0)
    df.to_csv(out_file)

    # dataframes for the periods
    dfs = {}
    for p in periods:
        #print p
        dfs[p] = pd.DataFrame(columns=heem_body_part_labels,
                              index=heem_emotion_labels)
    for em, ps in period_counters.iteritems():
        for p in ps:
            dfs[p].loc[em] = pd.Series(period_counters[em][p])

    path, bn = os.path.split(out_file)
    name = bn.replace('.csv', '')
    period_file_name_template = name+'_{}.csv'

    for p, dfp in dfs.iteritems():
        #print dfp
        dfp.fillna(0).to_csv(os.path.join(path,
                                          period_file_name_template.format(p)))
    #print period_counters['Liefde']
    #print dfs['enlightenment']
