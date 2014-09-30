#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to put a folia xml file in ElasticSearch.
"""
import os
import argparse
import time
from datetime import datetime
from elasticsearch import Elasticsearch
from lxml import etree
from bs4 import BeautifulSoup
from emotools.plays import extract_character_name, xml_id2play_id
from emotools.bs4_helpers import sentence, note, entity


def create_index(es, index_name, type_name):
    config = {}
    config['mappings'] = {
        type_name: {
            '_id': {
                'path': 'event_id'
            },
            'properties': {
                'event_id': {
                    'type': 'string',
                    'include_in_all': 'false',
                    'index': 'not_analyzed'
                },
                'text_id': {
                    'type': 'string',
                    'include_in_all': 'false',
                    'index': 'not_analyzed'
                },
                'event_class': {
                    'type': 'string',
                    'include_in_all': 'false',
                    'index': 'not_analyzed'
                },
                'actor': {
                    'type': 'string',
                    'include_in_all': 'false',
                    'index': 'not_analyzed'
                },
                'order': {
                    'type': 'integer',
                },
                'text': {
                    'type': 'string',
                    'include_in_all': 'false',
                    'index': 'analyzed'
                },
                'year': {
                    'type': 'integer',
                },
            }
        }
    }
    es.indices.create(index=index_name, body=config, ignore=400)
    # sleep to prevent error message when checking whether document exists
    time.sleep(2)


def event2es(event_xml, event_order, es, index_name, type_name):

    events = event_xml.find_all('event')
    event = events[0]
    event_id = event.attrs.get('xml:id')

    if not es.exists(index=index_name, doc_type=type_name, id=event_id):
        play_id = xml_id2play_id(event_id)

        cls = event.attrs.get('class')
        if cls == 'speakerturn':
            actor = extract_character_name(event.attrs.get('actor'))

        text = []
        for elem in event.descendants:
            if sentence(elem) and not note(elem.parent):
                text.append(elem.t.string)

        doc = {
            'event_id': event_id,
            'text_id': play_id,
            'event_class': cls,
            'order': event_order,
            'text': ' '.join(text)
        }
        if cls == 'speakerturn':
            doc['actor'] = actor

        es.index(index_name, type_name, doc)


def entities2es(event_xml, entity_class, timestamp, es, index_name, doc_type):
    events = event_xml.find_all('event')
    event = events[0]
    event_id = event.attrs.get('xml:id')

    entities = {}
    for elem in event.descendants:
        if entity(elem) and not note(elem.parent.parent.parent):
            ent_class = '{}-'.format(entity_class)
            if elem.get('class').startswith(ent_class):
                entity_name = elem.get('class').replace(ent_class, '')
                if not entities.get(entity_name):
                    entities[entity_name] = []
                entities[entity_name].append(elem.wref.get('t'))
    doc = {
        '{}-entities'.format(entity_class): {
            'data': entities,
            'timestamp': timestamp
        }
    }

    es.update(index=index_name,
              doc_type=type_name,
              id=event_id,
              body={'doc': doc})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='the name of the directory containing the '
                        'FoLiA XML files that should be processed')
    args = parser.parse_args()

    input_dir = args.dir

    # TODO: ES host + port as script arguments
    es = Elasticsearch()

    # TODO: index name as script argument
    index_name = 'embodied_emotions'
    type_name = 'event'
    create_index(es, index_name, type_name)

    event_tag = '{http://ilk.uvt.nl/folia}event'
    timestamp = datetime.now().isoformat()

    os.chdir(input_dir)
    counter = 0
    for file_name in os.listdir(input_dir):
        counter += 1
        print '({}) {}'.format(counter, file_name)

        # load document
        context = etree.iterparse(file_name,
                                  events=('start', 'end'),
                                  tag=event_tag,
                                  huge_tree=True)

        order = 0
        delete = True
        for event, elem in context:
            if event == 'start':
                delete = False
            if event == 'end':
                # ignore subevents
                if not elem.getparent().tag == event_tag:
                    order += 1
                    event_xml = BeautifulSoup(etree.tostring(elem), 'xml')
                    event2es(event_xml, order, es, index_name, type_name)
                    entities2es(event_xml, 'liwc', timestamp, es, index_name,
                                type_name)
                    delete = True

            if delete:
                elem.clear()
                while elem.getprevious() is not None:
                    del elem.getparent()[0]
        del context
