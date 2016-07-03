#import recipy
from codecs import open
import os
import glob
import json
import time
import pandas as pd
import click
import zipfile

from bs4 import BeautifulSoup
from random import randint
from collections import Counter

from embem.machinelearningdata.count_labels import corpus_metadata
from embem.emotools.heem_utils import heem_labels_en, heem_emotion_labels


def create_event(emotion_label, text_id, year):
    group_score = 100
    event_object = {
        'actors': {},
        'event': event_name(emotion_label, text_id),
        'group': emotion_label,
        'groupName': emotion_label,
        'groupScore': str(group_score),
        'labels': [],
        'mentions': [],
        'prefLabel': [],
        'time': "{}0101".format(year)
    }

    return event_object


def create_mention(emotion, soup, text_id, source):
    terms = [t['id'] for t in emotion.find_all('target')]
    tokens = [soup.find('term', id=t).span.target['id'] for t in terms]
    #sentence = soup.find('wf', id=tokens[0])['sent']

    if terms > 1:
        begin = soup.find('wf', id=tokens[0])['offset']
        wf = soup.find('wf', id=tokens[-1])
        end = int(wf['offset']) + int(wf['length'])
    else:
        wf = soup.find('wf', id=tokens[0])
        begin = int(wf['offset'])
        end = begin + int(wf['length'])
    chars = [str(begin), str(end)]

    mention = {
        'char': chars,
        'tokens': tokens,
        'uri': [str(text_id)],
        'perspective': [{'source': source}]
    }
    return mention


def get_label(soup, mention):
    label_parts = []
    for wid in mention['tokens']:
        word = soup.find('wf', id=wid).text
        label_parts.append(word)
    return ' '.join(label_parts)


def event_name(emotion_label, unique):
    return '{}_{}'.format(emotion_label, unique)


def process_emotions(soup, text_id, year, source, em_labels, confidence=0.5):
    assert confidence <= 1.0, 'Confidence threshold > 1.0'

    events = {}
    mention_counter = Counter()

    emotions = soup.find_all('emotion')
    print 'text contains {} emotions'.format(len(emotions))
    for emotion in emotions:
        # for some reason, BeautifulSoup does not see the capitals in
        # <externalRef>
        emotion_labels = emotion.find_all('externalref')
        for el in emotion_labels:
            c = float(el.get('confidence', 1.0))
            #print 'confidence', c
            #print 'over threshold', c >= confidence

            if el['resource'] == 'heem' and \
               el['reference'].split(':')[1] in em_labels and \
               c >= confidence:
                label = event_name(el['reference'].split(':')[1], text_id)

                if label not in events.keys():
                    #print 'created new event', label
                    events[label] = create_event(el['reference'].split(':')[1], text_id, year)
                m = create_mention(emotion, soup, text_id, source)
                mention_counter[label] += 1
                events[label]['mentions'].append(m)
                events[label]['labels'].append(get_label(soup, m))

        for el in emotion_labels:
            #print 'checking for bodyparts'
            c = float(el.get('confidence', 1.0))
            if el['resource'] == 'heem:bodyParts' and c >= confidence:
                #print 'found bodypart', el['reference']
                #print ems
                target_id = el.parent.parent.span.target['id']
                targets = soup.find_all('target', id=target_id)
                #print 'number of times target id used:', len(targets), target_id
                ems = []
                for target in targets:
                    #print target.parent.parent.externalreferences.find_all('externalref')
                    for l in target.parent.parent.externalreferences.find_all('externalref'):
                        #print l
                        c = float(l.get('confidence', 1.0))
                        if l['resource'] == 'heem' and c >= confidence:
                            name = l['reference'].split(':')[1]
                            if name in em_labels:
                                ems.append(name)

                #print ems
                for e in ems:
                    label = event_name(e, text_id)
                    if label not in events.keys():
                        #print 'created new event2', label
                        events[label] = create_event(e, text_id, year)
                    events[label]['actors'][el['reference']] = [el['reference']]
                    #print 'event'
                    #print events[e+text_id]
                    #print 'actors'
                    #print events[e+text_id]['actors']
                    #print 'actor value'
                    #print events[e+text_id]['actors'][el['reference']]
                    #print

    print 'found {} events and {} mentions'.format(len(mention_counter.keys()), sum(mention_counter.values()))
    print 'top three events: {}'.format(' '.join(['{} ({})'.format(k, v) for k, v in mention_counter.most_common(3)]))
    return events


def get_num_sentences(soup):
    return int((soup.find_all('wf')[-1]).get('sent'))


def get_text(soup):
    return ' '.join([wf.text for wf in soup.find_all('wf')])


def add_source_text(soup, text_id, json_object):
    json_object['timeline']['sources'].append({'uri': text_id,
                                               'text': get_text(soup)})


def add_events(events, num_sentences, json_object):
    for event, data in events.iteritems():
        add_climax_score(data, num_sentences)

        # TODO: make more intelligent choice for prefLabel (if possible)
        # Also, it seems that prefLabel is not used in the visualization
        data['prefLabel'] = [data['event']]
        json_object['timeline']['events'].append(data)


def merge_events(event1, event2):
    event = event1.copy()
    for k, v in event2['actors'].iteritems():
        event1['actors'][k] = v
    event['climax'] = event1['climax'] + event2['climax']
    # Do not change event, group, groupName, groupScore
    event['labels'] = event1['labels'] + event2['labels']
    event['mentions'] = event1['mentions'] + event2['mentions']
    # Do not change prefLabel, time

    return event


def add_climax_score(event, num_sentences):
    climax = len(event['mentions'])+0.0/num_sentences*100
    event['climax'] = climax


@click.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.argument('metadata', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
@click.option('--confidence', default=0.5, help='Confidence value threshold.')
def run(input_dir, metadata, output_dir, confidence):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    xml_files = glob.glob('{}/*.*'.format(input_dir))
    # The naf files containing predicted labels are stored in different
    # directories.
    if len(xml_files) == 0:
        xml_files = glob.glob('{}/*/*.*'.format(input_dir))

    text2period, text2year, text2genre, period2text, genre2text = \
        corpus_metadata(metadata)

    metadata = pd.read_csv(metadata, header=None, sep='\\t', index_col=0,
                           encoding='utf-8', engine='python')

    # the labels for which groups are created (emotion labels only)
    emotion_labels = [heem_labels_en[l].lower() for l in heem_emotion_labels]

    for i, fi in enumerate(xml_files):
        start = time.time()

        print '{} ({} of {})'.format(fi, (i + 1), len(xml_files))
        text_id = os.path.basename(fi).split('.')[0]
        text_id = text_id.rsplit('_', 1)[0]

        out_file = os.path.join(output_dir, '{}.json'.format(text_id))
        if not os.path.isfile(out_file):
            title = metadata.at[text_id, 3].decode('utf-8')
            author = metadata.at[text_id, 4]
            # compensate for the fact that the author field is sometines empty
            if author:
                author = author.decode('utf-8')
            source = u'{} - {}'.format(title, author)

            print text_id
            print source

            if zipfile.is_zipfile(fi):
                zf = zipfile.ZipFile(fi, 'r')
                xml = zf.read(zf.namelist()[0])
                soup = BeautifulSoup(xml, 'lxml')
            else:
                with open(fi, 'rb', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'lxml')

            year = text2year[text_id]
            num_sentences = get_num_sentences(soup)

            events = process_emotions(soup, text_id, year, source,
                                      emotion_labels, confidence)
            json_out = {
                'timeline': {
                    'events': [],
                    'sources': []
                }
            }

            add_events(events, num_sentences, json_out)
            add_source_text(soup, text_id, json_out)

            # write output
            with open(out_file, 'wb', encoding='utf-8') as f:
                json.dump(json_out, f, sort_keys=True, indent=4)

            end = time.time()
            print 'processing took {} sec.'.format(end-start)
        else:
            print 'File already processed...'


if __name__ == '__main__':
    run()
