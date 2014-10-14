#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to put a folia xml file in ElasticSearch.
"""
import codecs
import os
import time
from datetime import datetime
from elasticsearch import Elasticsearch, client
from lxml import etree
from bs4 import BeautifulSoup
from emotools.plays import extract_character_name, xml_id2play_id
from emotools.bs4_helpers import sentence, note, entity


if __name__ == '__main__':
    # Load liwc dict
    with codecs.open('historic_Dutch_LIWC.dic', 'rb', 'utf8') as f:
        lines = f.readlines()

    liwc_categories = {}
    liwc_dict = {}

    for line in lines:
        # LIWC category
        if line[0].isdigit():
            entry = line.split()
            # remove 0 from strings like 01
            c = str(int(entry[0]))
            liwc_categories[c] = entry[1]
        # word
        elif line[0].isalpha():
            entry = line.split()
            term = entry[0]
            categories = entry[1:]
            liwc_dict[term] = categories

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
    index_name = 'embodied_emotions'
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
            'words': words
        }
        es.index(index=index_name, doc_type=type_name, body=doc)
