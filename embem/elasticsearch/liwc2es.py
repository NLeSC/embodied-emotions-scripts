#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to put liwc entity categories in elasticsearch.
"""
import argparse
from elasticsearch import Elasticsearch
from embem.emotools.liwc_helpers import load_liwc

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dic', help='json file containing liwc dictionary '
                        '(e.g., <embem_data_dir>/dict/historic_'
                        'Dutch_LIWC.dic)')
    args = parser.parse_args()

    liwc_dict, liwc_categories = load_liwc(args.file, 'utf8')

    # Make dictionary of the form {liwc category: [word, word, word, ...]}
    liwc = {}
    for term, cats in liwc_dict.iteritems():
        for c in cats:
            cat = liwc_categories.get(c)
            if cat not in liwc.keys():
                liwc[cat] = []
            liwc[cat].append(term)

    # TODO: ES host + port as script arguments
    es = Elasticsearch()

    # TODO: index name as script argument
    index_name = 'embem'
    type_name = 'entitycategory'

    mapping = {
        'entitycategory': {
            '_id': {
                'path': 'name'
            },
            'properties': {
                'name': {
                    'type': 'string',
                    'index': 'not_analyzed'
                },
                'es_name': {
                    'type': 'string',
                    'index': 'not_analyzed'
                },
                'words': {
                    'type': 'string',
                    'index': 'not_analyzed'
                },
            }
        }
    }
    es.indices.put_mapping(index=index_name, doc_type=type_name, body=mapping)

    for cat, words in liwc.iteritems():
        print cat
        doc = {
            'name': cat,
            'es_name': 'liwc-entities.data.{}'.format(cat),
            'words': words
        }
        es.index(index=index_name, doc_type=type_name, body=doc)
