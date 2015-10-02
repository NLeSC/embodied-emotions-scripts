"""Generate json objects storing the label replacements for diffent
subdivisions of the emotion labels.

Usage: python generate_labels_json.py <output dir>

The replacements are only stored if the relevant file does not yet exist.
"""

from random import shuffle
import json
import codecs
import os.path
import argparse

_replacements_clusters = {
    'Love': ['Liefde', 'Trouw', 'Toewijding'],
    'Compassion': ['Mededogen'],
    'Sadness': ['Verdriet', 'Bedruktheid', 'Teleurstelling', 'Gemis',
                'Wroeging'],
    'Fear': ['Angst', 'Bezorgdheid', 'Achterdocht', 'Ontzag'],
    'Joy': ['Blijdschap', 'Geluk', 'Hoop', 'Opluchting', 'Verwondering'],
    'Despair': ['Wanhoop', 'Ongeluk'],
    'Anger': ['Woede', 'Haat', 'Wrevel', 'Wrok', 'Beledigd', 'Wraakzucht'],
    'Desire': ['Verlangen', 'Hebzucht', 'Jaloezie'],
    'Disgust': ['Walging', 'Schaamte'],
    'PosSentiments': ['Ontroering', 'Berusting', 'Vertrouwen',
                      'Welwillendheid'],
    'PrideHonour': ['Trots', 'Eergevoel']
}

_replacements_posneg = {
    'Negative': ['Verdriet', 'Angst', 'Woede', 'Wanhoop', 'Wraakzucht',
                 'Haat', 'Wroeging', 'Schaamte', 'Bezorgdheid', 'Walging',
                 'Bedruktheid', 'Beledigd', 'Wrok', 'Achterdocht',
                 'Jaloezie', 'Wrevel', 'Ongeluk', 'Gemis',
                 'Teleurstelling', 'Hebzucht'],
    'Positive': ['Liefde', 'Blijdschap', 'Verlangen', 'Mededogen', 'Hoop',
                 'Eergevoel', 'Ontroering', 'Trouw', 'Verwondering',
                 'Geluk', 'Berusting', 'Toewijding', 'Ontzag',
                 'Welwillendheid', 'Opluchting', 'Trots', 'Vertrouwen']
}

_emotion_labels = ['Verdriet', 'Angst', 'Woede', 'Wanhoop', 'Wraakzucht',
                   'Haat', 'Wroeging', 'Schaamte', 'Bezorgdheid', 'Walging',
                   'Bedruktheid', 'Beledigd', 'Wrok', 'Achterdocht',
                   'Jaloezie', 'Wrevel', 'Ongeluk', 'Gemis', 'Teleurstelling',
                   'Hebzucht', 'Liefde', 'Blijdschap', 'Verlangen',
                   'Mededogen', 'Hoop', 'Eergevoel', 'Ontroering', 'Trouw',
                   'Verwondering', 'Geluk', 'Berusting', 'Toewijding',
                   'Ontzag', 'Welwillendheid', 'Opluchting', 'Trots',
                   'Vertrouwen']


def write_to_file(fname, replacements):
    if not os.path.isfile(fname):
        with codecs.open(fname, 'wb', 'utf8') as f:
            json.dump(replacements, f, encoding='utf8', indent=2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('out_dir', help='directory output should be saved to')
    args = parser.parse_args()

    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)

    write_to_file('{}/heem_clusters.json'.format(args.out_dir),
                  _replacements_clusters)
    write_to_file('{}/posneg.json'.format(args.out_dir),
                  _replacements_posneg)
