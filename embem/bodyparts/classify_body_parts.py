"""Find known body parts in sentences with predicted label 'Lichaamsdeel'.

Extended body parts are saved to new text files.

Usage: python classify_body_parts.py <json file with body part mapping> <dir
with input texts> <dir for output texts>
"""
import os
import codecs
import argparse
import json
from embem.machinelearningdata.count_labels import load_data
import pandas as pd


def extend_body_part(text_id, file_name, out_file, word2cat):
    # load data set
    X_data, Y_data = load_data(file_name)

    Y = [s.split('_') for s in Y_data]

    num_body_parts = 0
    num_added = 0

    with codecs.open(out_file, 'wb', 'utf-8') as f:
        for i, labelset in enumerate(Y):
            ls = labelset
            if 'Lichaamsdeel' in labelset:
                num_body_parts += 1
                words = X_data[i].split()
                added = False
                for word in words:
                    w = word.lower()
                    if w in word2cat.keys():
                        ls.append(word2cat[w].capitalize())
                        added = True
                if added:
                    num_added += 1
            ls = sorted(list(set(ls)))
            f.write(u'{}\t{}\n'.format(X_data[i].decode('utf-8'),
                                       '_'.join(ls)))
    return text_id, num_body_parts, num_added


def get_extended_body_part_mapping(file_name):
    mapping = {}

    # read body part mapping
    with codecs.open(file_name, 'rb', 'utf8') as f:
        mapping = json.load(f, encoding='utf8')

    # reverse body part mapping
    word2cat = {}
    for la, ws in mapping.iteritems():
        for word in ws:
            if not word2cat.get(word):
                word2cat[word] = la
            else:
                print 'ignored: {} ({})'.format(word, la)
    return word2cat


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='json file containing the body part '
                        'mapping.')
    parser.add_argument('input_dir', help='the directory where the input text '
                        'files can be found.')
    parser.add_argument('output_dir', help='the directory where the output '
                        'files should be written.')
    parser.add_argument('output_file', help='file to store the statistics '
                        'on body part expansions')
    args = parser.parse_args()

    file_name = args.file
    input_dir = args.input_dir
    output_dir = args.output_dir
    output_file = args.output_file

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    word2cat = get_extended_body_part_mapping(file_name)

    data = {'#body_parts': [], '#replaced': []}
    index = {'text_id': []}
    # process texts
    text_files = [t for t in os.listdir(input_dir) if t.endswith('.txt')]
    for text_file in text_files:
        text_id = text_file.replace('.txt', '')
        in_file = os.path.join(input_dir, text_file)
        out_file = os.path.join(output_dir, text_file)

        text_id, num_body_parts, num_added = extend_body_part(text_id,
                                                              in_file,
                                                              out_file,
                                                              word2cat)
        index['text_id'].append(text_id)
        data['#body_parts'].append(num_body_parts)
        data['#replaced'].append(num_added)

    # save statistics
    df = pd.DataFrame(data=data, index=index['text_id'])
    df.to_csv(output_file)
