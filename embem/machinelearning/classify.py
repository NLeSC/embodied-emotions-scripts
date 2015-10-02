"""Script to classify new data
"""
import argparse
import os
import codecs

from sklearn.externals import joblib

from mlutils import get_data, load_data


parser = argparse.ArgumentParser()
parser.add_argument('in_dir', help='directory containing txt files for '
                    'prediction')
parser.add_argument('out_dir', help='directory to write output to')
parser.add_argument('train_file', help='train file used to train the '
                    'classifier (used to extract the class labels)')
parser.add_argument('classifier', help='classifier file')
args = parser.parse_args()

if not os.path.exists(args.out_dir):
    os.makedirs(args.out_dir)

# load classifier
clf = joblib.load(args.classifier)

text_files = [fi for fi in os.listdir(args.in_dir) if fi.endswith('.txt')]
for i, text_file in enumerate(text_files):
    in_file = os.path.join(args.in_dir, text_file)
    print '{} of {}'.format(i+1, len(text_files))
    print 'In:', in_file

    # load data
    X_train, X_data, Y_train, Y_data, classes_ = get_data(args.train_file,
                                                          in_file)

    # classifiy
    pred = clf.predict(X_data)

    # save results
    out_file = os.path.join(args.out_dir, text_file)
    print 'Out:', out_file

    X_data_with_ids, Y_data = load_data(in_file)

    with codecs.open(out_file, 'wb', 'utf8') as f:
        for x, y in zip(X_data_with_ids, pred):
            f.write(u'{}\t{}\n'.format(x.decode('utf8'),
                                       '_'.join(classes_[y]) or 'None'))

    print
