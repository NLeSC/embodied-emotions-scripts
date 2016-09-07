#import recipy
from codecs import open
import os
import glob
import json
import time
import pandas as pd
import click
import zipfile
import sys
import copy
import re

from lxml import etree
from collections import Counter

from embem.machinelearningdata.count_labels import corpus_metadata
from embem.emotools.heem_utils import heem_labels_en, heem_emotion_labels


json_out = {
    'timeline': {
        'events': [],
        'sources': []
    }
}

def create_event(emotion_label, text_id, year, bodyparts):
    group_score = 100
    actors = {}
    for bp in bodyparts:
        actors[bp] = bp
    event_object = {
        'actors': actors,
        'event': event_name(emotion_label, bodyparts, text_id),
        'group': emotion_label,
        'groupName': emotion_label,
        'groupScore': str(group_score),
        'labels': [],
        'mentions': [],
        'prefLabel': [],
        'time': "{}0101".format(year)
    }

    return event_object


def create_mention(emotion, termid2tokenid, tokenid2token, text_id, source,
                   sentences):
    terms = emotion['terms']
    tokens = [termid2tokenid[t] for t in terms]
    #sentence = soup.find('wf', id=tokens[0])['sent']

    begin = tokenid2token[termid2tokenid[terms[0]]]['offset']
    end = tokenid2token[termid2tokenid[terms[-1]]]['offset'] + tokenid2token[termid2tokenid[terms[-1]]]['length']
    chars = [str(begin), str(end)]

    s = sentences[tokenid2token[termid2tokenid[terms[0]]]['sentence']]
    #print s

    mention = {
        'char': chars,
        'tokens': tokens,
        'uri': [str(text_id)],
        'perspective': [{'source': source}],
        'snippet': [s],
        'snippet_char': [1, 2]
    }
    return mention


def get_label(tokenid2token, mention):
    words = [tokenid2token[tid]['text'] for tid in mention['tokens']]

    return ' '.join(words)


def add_snippet_chars(mention, text):
    #print text
    m = re.search(re.escape(text), mention['snippet'][0])
    if m:
        mention['snippet_char'] = list(m.span())


def remove_tokens(mention):
    del mention['tokens']


def event_name(emotion_label, bodyparts, unique):
    return '{}_{}_{}'.format(emotion_label, '-'.join(bodyparts), unique)


def process_emotions(text_id, year, source, em_labels, sentences,
                     tokenid2token, termid2tokenid, termid2emotionid, emotions,
                     emoids, confidence=0.5):
    assert confidence <= 1.0, 'Confidence threshold > 1.0'

    events = {}
    mention_counter = Counter()

    print 'text contains {} emotions'.format(len(emotions.keys()))
    for emoid in emoids:
        #print emoid
        emotion = emotions[emoid]

        emotion_labels = emotion['heem labels']
        bps = [el['reference'] for el in emotion_labels if el['resource'] == 'heem:bodyParts']
        #print bps
        for el in emotion_labels:
            c = el['confidence']
            #print 'confidence', c
            #print 'over threshold', c >= confidence

            if el['resource'] == 'heem' and \
               el['reference'].split(':')[1] in em_labels and \
               c >= confidence:
                label = event_name(el['reference'].split(':')[1], bps, text_id)

                if label not in events.keys():
                    #print 'created new event', label
                    events[label] = create_event(el['reference'].split(':')[1], text_id, year, bps)
                m = create_mention(emotion, termid2tokenid, tokenid2token, text_id, source, sentences)
                mention_counter[label] += 1
                mt = get_label(tokenid2token, m)
                add_snippet_chars(m, mt)
                remove_tokens(m)
                events[label]['mentions'].append(m)
                events[label]['labels'].append(mt)

    print 'found {} events and {} mentions'.format(len(mention_counter.keys()), sum(mention_counter.values()))
    print 'top three events: {}'.format(' '.join(['{} ({})'.format(k, v) for k, v in mention_counter.most_common(3)]))
    return events, len(emotions)


def add_source_text(text, text_id, json_object):
    json_object['timeline']['sources'].append({'uri': text_id,
                                               'text': text})


def add_events(events, num_sentences, json_object):
    for event, data in events.iteritems():
        add_climax_score(data, num_sentences)

        # TODO: make more intelligent choice for prefLabel (if possible)
        # Also, it seems that prefLabel is not used in the visualization
        data['prefLabel'] = [data['event']]
        json_object['timeline']['events'].append(data)


def merge_events(event1, event2):
    event = copy.deepcopy(event1)
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


def merge_emotions(em1, em2):
    e = {
        'terms': em1.get('terms'),
        'heem labels': em1.get('heem labels') + em2.get('heem labels')
    }
    return e


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
        if text_id.endswith('_01'):
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
                lxmlsoup = etree.fromstring(xml)
            else:
                with open(fi, 'rb', encoding='utf-8') as f:
                    lxmlsoup = etree.parse(f)

            year = text2year[text_id]

            tokenid2token = {}
            tokens = lxmlsoup.findall('.//wf')
            words = []
            num_sentences = int(tokens[-1].get('sent'))
            s_id = tokens[-1].get('sent')
            s = []
            sentences = {}
            #print num_sentences
            #print len(tokens)
            for token in tokens:
                if s_id != token.get('sent'):
                    sentences[s_id] = ' '.join(s)
                    s = []
                    s_id = token.get('sent')
                tokenid = token.get('id')
                tokenid2token[tokenid] = {
                    'text': token.text,
                    'offset': int(token.get('offset')),
                    'length': int(token.get('length')),
                    'sentence': token.get('sent')
                }
                words.append(token.text)
                s.append(token.text)
                #print tokenid2token[tokenid]
            text = ' '.join(words)

            termid2tokenid = {}
            terms = lxmlsoup.findall('.//term')
            for term in terms:
                termid = term.get('id')
                tokenid = term[0][0].get('id')
                termid2tokenid[termid] = tokenid
                #print termid, tokenid

            termid2emotionid = {}
            emotions = {}
            emoids = []
            xml_emotions = lxmlsoup.findall('.//emotion')
            for e in xml_emotions:
                emotionid = e.get('id')
                xml_emotion = etree.fromstring(etree.tostring(e))
                terms = xml_emotion.findall('.//target')
                labels = xml_emotion.findall('.//externalRef')
                for t in terms:
                    termid = t.get('id')
                    if termid not in termid2emotionid.keys():
                        termid2emotionid[termid] = []
                    termid2emotionid[termid].append(emotionid)

                ls = [{'reference': l.get('reference'),
                       'resource': l.get('resource'),
                       'confidence': float(l.get('confidence', 1.0))} for l in labels]
                emotions[emotionid] = {
                    'terms': [t.get('id') for t in terms],
                    'heem labels': ls
                }
                # to make sure the order of emotions is the same as before
                # (so the resulting json is exactly the same)
                emoids.append(emotionid)

            print len(emoids)
            for term, ems in termid2emotionid.iteritems():
                if len(ems) == 2:
                    if emotions.get(ems[0]) and emotions.get(ems[1]):
                        if len(emotions.get(ems[0]).get('terms')) > len(emotions.get(ems[1]).get('terms')):
                            em1, em2 = ems
                        else:
                            em2, em1 = ems
                        #print 'merging', em1, em2
                        #print emotions[em1]
                        #print emotions[em2]
                        emotions[em1] = merge_emotions(emotions[em1], emotions[em2])
                        #print emotions[em1]
                        del emotions[em2]
                        emoids.remove(em2)
                    else:
                        print 'not merging', ems[0], ems[1]

                elif len(ems) > 2:
                    print 'Found a term that points to more than 2 emotions'
                    print term
                    print ems
                    sys.exit()

            print len(emoids)

            events, num_emotions = process_emotions(text_id, year, source,
                                                    emotion_labels,
                                                    sentences,
                                                    tokenid2token,
                                                    termid2tokenid,
                                                    termid2emotionid, emotions,
                                                    emoids, confidence)

            out = copy.deepcopy(json_out)
            add_events(events, num_sentences, out)
            #add_source_text(text, text_id, out)

            # write output
            with open(out_file, 'wb', encoding='utf-8') as f:
                json.dump(out, f, sort_keys=True, indent=4)

            end = time.time()
            print 'processing took {} sec.'.format(end-start)
            print '({} seconds on average per emotion)'.format((end-start)/num_emotions)
        else:
            print 'File already processed...'


if __name__ == '__main__':
    run()
