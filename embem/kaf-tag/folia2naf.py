"""Create a NAF file for FoLiA files containing embodied emotions annotations.
Usage: python folia2naf.py <dir in> <corpus metadata csv> <dir out>
"""
from lxml import etree
from bs4 import BeautifulSoup
from embem.emotools.bs4_helpers import act, sentence, note
from embem.emotools.heem_utils import heem_emotion_labels, heem_labels_en, \
    heem_modifiers_en
from folia2kaf import xml2kafnaf
import argparse
import os
import sys
import glob
from collections import Counter
import pandas as pd
import datetime
from embem.machinelearningdata.count_labels import corpus_metadata

emotions_labels = ['Emotie', 'Lichaamswerking', 'EmotioneleHandeling']
markables_labels = ['Lichaamsdeel', 'HumorModifier', 'Intensifier']

genres_en = {'blijspel / komedie': 'comedy',
             'tragedie/treurspel': 'tragedy',
             'klucht': 'farce',
             'Anders': 'other',
             'unknown': 'unknown'}


def embem_entity(elem):
    if elem.get('class').startswith('EmbodiedEmotions'):
        return True
    return False


def contains_markable(entities):
    entity_labels = [ent.get('class') for ent in entities]
    for l1 in entity_labels:
        for l2 in markables_labels:
            if l2 in l1:
                return True
    return False


def contains_emotion(entities):
    labels = [ent.get('class').split(':')[1] for ent in entities]

    #if bool(set(labels) & set(emotions_labels)):
        #print 'Emotion!'

    return bool(set(labels) & set(emotions_labels))


def lowerc(str):
    """Lowercase first character of input string"""
    return str[0].lower() + str[1:]


def add_targets(elem, words, wids):
    span = etree.SubElement(elem, 'span')
    # words
    span.append(etree.Comment(' ' + ' '.join(words) + ' '))
    # word ids (targets)
    for wid in wids:
        etree.SubElement(span, 'target', id=wid)


def add_emoVal(elem, value, resource, confidence):
    etree.SubElement(elem, 'emoVal', value=value, confidence=confidence,
                     resource=resource)


def naf_markable(data):
    markable = etree.Element('markable')
    add_targets(markable, data['words'], data['wids'])

    # emovals
    for label in data['labels']:
        last_part = label.split(':')[1]
        if label.endswith('Lichaamsdeel'):
            l = heem_labels_en['Lichaamsdeel']
            l = lowerc(l)
            r = 'embemo:conceptType'
        elif label.split(':')[1] in heem_emotion_labels:
            l = heem_labels_en[last_part]
            l = lowerc(l)
            r = 'embemo:emotionType'
        else:
            parts = label.split('-')[1].split(':')
            l = parts[1]
            if l in heem_modifiers_en.keys():
                l = heem_modifiers_en[l]
                l = lowerc(l)
                r = 'embemo:{}'.format(lowerc(parts[0]))
                # make list of all modifiers
                modifiers[l] += 1
                #print l, r
            else:
                l = None
        if l and r:
            add_emoVal(markable, l, r, '1.0')
    return markable


def naf_emotion(data, emo_id):
    eid = 'emo{}'.format(emo_id)
    emotion = etree.Element('emotion', id=str(eid))
    etree.SubElement(emotion, 'emotion_target')
    etree.SubElement(emotion, 'emotion_holder')
    expr = etree.SubElement(emotion, 'emotion_expression')

    add_targets(emotion, data['words'], data['wids'])

    # emovals
    for label in data['labels']:
        l = label.split(':')[1]
        l = heem_labels_en.get(l)
        if l:
            l = lowerc(l)
            if l in heem_emotion_labels:
                r = 'embemo:emotionType'
            else:
                r = 'embemo:conceptType'
            add_emoVal(emotion, l, r, '1.0')
    if not l:
        emotion = None
    emo_id += 1

    return emotion, emo_id


def emotions2naf(emotions, markables, elem, emo_id):
    entity_tag = '{http://ilk.uvt.nl/folia}entity'
    wref_tag = '{http://ilk.uvt.nl/folia}wref'

    added = {}

    entities = [e for e in elem.findall(entity_tag) if embem_entity(e)]

    emotion_values = {}
    for ent in entities:
        ids = [wref.get('id') for wref in ent.findall(wref_tag)]
        x = ''.join(ids)
        if not x in emotion_values.keys():
            words = [wref.get('t') for wref in ent.findall(wref_tag)]
            emotion_values[x] = {'labels': [], 'wids': ids, 'words': words,
                                 'entities': []}
        emotion_values[x]['labels'].append(ent.get('class'))
        emotion_values[x]['entities'].append(ent)

    for key, data in emotion_values.iteritems():
        if contains_markable(data['entities']):
            #print 'Add markable!'
            markables.append(naf_markable(data))
        if contains_emotion(data['entities']) or \
            (not contains_emotion(data['entities']) and
             not contains_markable(data['entities'])):
            # Add entity as emotion if it contains an emotion.
            # The data set contains words tagged with only an emotion label
            # These annotations are also added as emotion
            #print 'Add emotion!'
            #print [(e.tag, e.attrib) for e in data['entities']]
            emotion, emo_id = naf_emotion(data, emo_id)
            if emotion is not None:
                emotions.append(emotion)

    return emo_id


def create_naf():
    root = etree.Element('NAF', lang='nl', version='v4')
    naf_document = etree.ElementTree(root)
    header = etree.SubElement(root, 'nafHeader')
    text = etree.SubElement(root, 'text')
    terms = etree.SubElement(root, 'terms')
    emotions_layer = etree.SubElement(root, 'emotions')

    return root, naf_document, header, text, terms, emotions_layer


def create_fileDesc(xml_file, text_id, metadata_file, timestamp, header):
    fname = os.path.basename(xml_file)

    text2period, text2year, text2genre, period2text, genre2text = \
        corpus_metadata(metadata_file)
    year = text2year[text_id]
    genre = genres_en.get(text2genre[text_id], 'unknown')
    metadata = pd.read_csv(metadata_file, header=None, sep='\\t', index_col=0,
                           encoding='utf-8')
    title = metadata.at[text_id, 3].decode('utf-8')
    author = metadata.at[text_id, 4].decode('utf-8')
    etree.SubElement(header, 'fileDesc', creationtime=timestamp,
                     title=unicode(title), author=unicode(author),
                     filename=fname, filetype='FoLiA/XML', year=year,
                     genre=genre)


def create_public(text_id, header):
    uri = 'http://dbnl.nl/titels/titel.php?id={}'.format(text_id)
    etree.SubElement(header, 'public', publicId=text_id, uri=uri)


def create_linguisticProcessor(xml_file, layer, name, version, timestamp,
                               header):
    ctime = str(datetime.datetime.fromtimestamp(os.path.getmtime(xml_file)))
    lp = etree.SubElement(header, 'linguisticProcessors', layer=layer)
    etree.SubElement(lp, 'lp', name=name, version=version, timestamp=ctime)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='directory containing FoLiA XML '
                        'files containing annotations')
    parser.add_argument('metadata', help='the name of the csv file containing '
                        'collection metadata')
    parser.add_argument('output_dir', help='the directory where the '
                        'generated KAF files should be saved')
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    xml_files = glob.glob('{}/*.xml'.format(input_dir))

    act_tag = '{http://ilk.uvt.nl/folia}div'
    entities_tag = '{http://ilk.uvt.nl/folia}entities'
    annotation_tag = '{http://ilk.uvt.nl/folia}token-annotation'

    modifiers = Counter()

    for i, f in enumerate(xml_files):
        print '{} ({} of {})'.format(f, (i + 1), len(xml_files))
        text_id = f[-20:-7]

        # reset linguisting processor terms datetime
        lp_terms_datetime = ''

        # Load document
        context = etree.iterparse(f, events=('end',),
                                  tag=(act_tag, entities_tag, annotation_tag))

        s_id = 0  # in KAF, sentence numbers must be integers
        term_id = 1
        emo_id = 1

        # create output naf xml tree
        root, naf_document, header, text, terms, emotions_layer = create_naf()

        ctime = str(datetime.datetime.fromtimestamp(os.path.getmtime(f)))

        create_fileDesc(f, text_id, args.metadata, ctime, header)
        create_public(text_id, header)
        create_linguisticProcessor(f, 'emotions',
                                   'Embodied Emotions Annotations', '1.0',
                                   ctime, header)

        emotions = []
        markables = []

        for event, elem in context:
            if elem.tag == act_tag and elem.get('class') == 'act':
                # load act into memory
                act_xml = BeautifulSoup(etree.tostring(elem), 'xml')
                subacts = act_xml.find_all(act)
                # act_xml should contain exactly one act; if it contains more
                # acts, these acts are sub acts, that will be processed later
                if len(subacts) == 1:
                    print 'act:', act_xml.find('div', 'act').attrs.\
                          get('xml:id')
                    s_id, term_id = xml2kafnaf(act_xml, s_id, term_id, text,
                                               terms)
            elif elem.tag == entities_tag:
                emo_id = emotions2naf(emotions, markables, elem, emo_id)
            elif elem.tag == annotation_tag:
                lp_terms_datetime = elem.attrib.get('datetime')

        # linguistic processors for terms
        generator = context.root.attrib.get('generator')
        name, version = generator.split('-')
        create_linguisticProcessor(f, 'terms', name, version,
                                   lp_terms_datetime, header)

        # add emotions layer
        for t in emotions + markables:
            emotions_layer.append(t)

        # save naf document
        out_file = os.path.basename(f)
        xml_out = os.path.join(output_dir, out_file)
        print 'writing', xml_out
        naf_document.write(xml_out, xml_declaration=True, encoding='utf-8',
                           method='xml', pretty_print=True)
        print

    # save list of modifiers/intensifiers
    out_file = os.path.join(output_dir, '_modifiers.csv')
    data = pd.DataFrame.from_dict(modifiers, orient='index').reset_index()
    data.to_csv(out_file, encoding='utf-8')
