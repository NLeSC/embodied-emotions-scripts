import codecs
import argparse
import os
import glob
import json
import time

from bs4 import BeautifulSoup
from random import randint

from embem.machinelearningdata.count_labels import corpus_metadata


def create_event(emotion_label, text_id, year):
    group_score = 100
    event_object = {
        'actors': {},
        'event': emotion_label,
        'group': "{}:{}".format(group_score, text_id),
        'groupName': text_id,
        'groupScore': str(group_score),
        'labels': [],
        'mentions': [],
        'prefLabel': [],
        'time': "{}0000".format(year)
    }

    return event_object


def create_mention(emotion, soup, text_id):
    terms = [t['id'] for t in emotion.find_all('target')]
    tokens = [soup.find('term', id=t).span.target['id'] for t in terms]
    sentence = soup.find('wf', id=tokens[0])['sent']

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
        'sentence': sentence,
        'terms': terms,
        'tokens': tokens,
        'uri': [str(text_id)]
    }
    return mention


def get_label(soup, mention):
    label_parts = []
    for wid in mention['tokens']:
        word = soup.find('wf', id=wid).text
        label_parts.append(word)
    return ' '.join(label_parts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='directory containing naf XML files')
    parser.add_argument('metadata', help='the name of the csv file containing '
                        'collection metadata')
    parser.add_argument('output_file', help='filename of the output (.json)')
    args = parser.parse_args()

    input_dir = args.input_dir
    output_file = args.output_file
    output_dir = os.path.dirname(output_file)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    xml_files = glob.glob('{}/*.xml'.format(input_dir))

    text2period, text2year, text2genre, period2text, genre2text = \
        corpus_metadata(args.metadata)

    events = {}
    json_out = {
        'timeline': {
            'events': [],
            'sources': []
        }
    }

    for i, fi in enumerate(xml_files):
        start = time.time()

        print '{} ({} of {})'.format(fi, (i + 1), len(xml_files))
        text_id = fi[-20:-7]

        print text_id

        with codecs.open(fi, 'rb', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'lxml')

        num_sentences = int((soup.find_all('wf')[-1]).get('sent'))

        emotions = soup.find_all('emotion')
        for emotion in emotions:
            # for some reason, BeautifulSoup does not see the capitals in
            # <externalRef>
            emotion_labels = emotion.find_all('externalref')
            ems = [l['reference'] for l in emotion_labels if l['reference'].startswith('emotionType:')]
            for el in emotion_labels:
                if el['resource'] == 'heem':
                    label = el['reference']+text_id

                    if label not in events.keys():
                        #print 'created new event', label
                        year = text2year[text_id]
                        events[label] = create_event(label, text_id, year)
                    m = create_mention(emotion, soup, text_id)
                    events[label]['mentions'].append(m)
                    events[label]['labels'].append(get_label(soup, m))

            for el in emotion_labels:
                #print 'checking for bodyparts'
                if el['resource'] == 'heem:bodyParts':
                    #print 'found bodypart', el['reference']
                    #print ems
                    for e in ems:
                        events[e+text_id]['actors'][el['reference']] = [el['reference']]
                        #print 'event'
                        #print events[e+text_id]
                        #print 'actors'
                        #print events[e+text_id]['actors']
                        #print 'actor value'
                        #print events[e+text_id]['actors'][el['reference']]
                        #print

        end = time.time()
        print 'processing took {} sec.'.format(end-start)

        text = ' '.join([wf.text for wf in soup.find_all('wf')])
        json_out['timeline']['sources'].append({'uri': text_id, 'text': text})

        for event, data in events.iteritems():
            data['climax'] = len(data['mentions'])+0.0/num_sentences*100

            # TODO: make more intelligent choice for prefLabel (if possible)
            # Also, it seems that prefLabel is not used in the visualization
            data['prefLabel'] = [data['event']]
            json_out['timeline']['events'].append(data)

        # write temporary output
        temp_output_file = output_file.replace('.json', '{}.json'.format(i))
        print temp_output_file
        with codecs.open(temp_output_file, 'wb', encoding='utf-8') as f:
            json.dump(json_out, f, sort_keys=True, indent=4)

    # write output
    with codecs.open(output_file, 'wb', encoding='utf-8') as f:
        json.dump(json_out, f, sort_keys=True, indent=4)
