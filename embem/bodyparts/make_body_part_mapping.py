"""Make a mapping from body part words to categories.

Make mapping <body part word> -> [historic words] based on Inger Leemans'
clustering.

Usage: python make_body_part_mapping.py

Requires files body_part_clusters_renaissance.csv,
body_part_clusters_classisism.csv, and body_part_clusters_enlightenment.csv to 
be in the current directory.

Writes body_part_mapping.json to the current directory.
"""

import codecs
import json


def csv2mapping(file_name):
    mapping = {}

    with codecs.open(file_name, 'rb', 'utf-8') as f:
        for line in f.readlines():
            parts = line.split(';')
            label = parts[0].lower()
            if parts[2] != '':
                if not mapping.get(label):
                    mapping[label] = []
                for entry in parts[2:]:
                    if entry and entry != '\n':
                        words = entry.split('\t')
                        mapping[label].append(words[0])

    return mapping


def merge_mappings(m1, m2):
    for k, v in m2.iteritems():
        if not m1.get(k):
            m1[k] = v
        else:
            m1[k] = m1[k] + v
    return m1


mapping_r = csv2mapping('body_part_clusters_renaissance.csv')
mapping_c = csv2mapping('body_part_clusters_classisism.csv')
mapping_e = csv2mapping('body_part_clusters_enlightenment.csv')

mapping = merge_mappings(mapping_r, mapping_c)
mapping = merge_mappings(mapping, mapping_e)

for k, v in mapping.iteritems():
    mapping[k] = list(set(mapping[k]))

with codecs.open('body_part_mapping.json', 'wb', 'utf-8') as f:
    json.dump(mapping, f, indent=2)
