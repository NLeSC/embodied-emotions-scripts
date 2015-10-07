"""Create a KAF file for each act in a FoLiA file
Usage: python folia2kaf.py <file in> <output dir>
Or: ./generate_kaf.sh <dir in> <dir out>
"""
from lxml import etree
from bs4 import BeautifulSoup
from embem.emotools.bs4_helpers import act, sentence, note
from folia2kaf import xml2kafnaf
import argparse
import os
import sys

emotions_labels = ['Emotie', 'Lichaamswerking', 'EmotioneleHandeling']
markables_labels = ['Lichaamsdeel', 'HumorModifier', 'Intensifier']


def embem_entity(elem):
    if elem.get('class').startswith('EmbodiedEmotions'):
        return True
    return False


def contains_markable(entities):
    entity_labels = [ent.get('class') for ent in entities]
    for l1 in entity_labels:
        for l2 in markables_labels:
            if l2 in l1:
                print 'markable!', l1, l2
                return True
    return False


def contains_emotion(entities):
    labels = [ent.get('class').split(':')[1] for ent in entities]

    if bool(set(labels) & set(emotions_labels)):
        print 'Emotion!'

    return bool(set(labels) & set(emotions_labels))


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
            print 'Add markable!'
            markable = etree.Element('markable')
            span = etree.SubElement(markable, 'span')
            # words
            span.append(etree.Comment(' '+' '.join(data['words'])+' '))
            # word ids (targets)
            for wid in data['wids']:
                etree.SubElement(span, 'target', id=wid)
            # emovals
            for label in data['labels']:
                l = label.split(':')[1]
                etree.SubElement(markable, 'emoVal', value=l,
                                 confidence='1.0', resource='bla')
            markables.append(markable)
        else:
            # If it is not a markable, we assume that it is an emotion
            # The data set contains words tagged with only an emotion label
            # These words are added as emotion
            print 'Add emotion!'
            eid = 'emo{}'.format(emo_id)
            emotion = etree.Element('emotion', id=str(eid))
            etree.SubElement(emotion, 'emotion_target')
            etree.SubElement(emotion, 'emotion_holder')
            expr = etree.SubElement(emotion, 'emotion_expression')

            span = etree.SubElement(expr, 'span')
            # words
            span.append(etree.Comment(' '+' '.join(data['words'])+' '))
            # word ids (targets)
            for wid in data['wids']:
                etree.SubElement(span, 'target', id=wid)
            # emovals
            for label in data['labels']:
                l = label.split(':')[1]
                etree.SubElement(emotion, 'emoVal', value=l,
                                 confidence='1.0', resource='bla')
            emotions.append(emotion)
            emo_id += 1

    return emo_id


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='the name of the FoLiA XML file to '
                        'generate KAF files for')
    parser.add_argument('output_dir', help='the directory where the '
                        'generated KAF files should be saved')
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    file_name = input_dir

    act_tag = '{http://ilk.uvt.nl/folia}div'
    entities_tag = '{http://ilk.uvt.nl/folia}entities'

    # Load document
    context = etree.iterparse(file_name, events=('end',),
                              tag=(act_tag, entities_tag))

    act_number = 0

    s_id = 0  # in KAF, sentence numbers must be integers
    term_id = 1
    emo_id = 1

    # create output naf xml tree for act
    root = etree.Element('NAF')
    naf_document = etree.ElementTree(root)
    text = etree.SubElement(root, 'text')
    terms = etree.SubElement(root, 'terms')
    emotions_layer = etree.SubElement(root, 'emotions')

    # TODO: nafheader with fileDesc and linguistic processors

    emotions = []
    markables = []

    for event, elem in context:
        if elem.tag == act_tag and elem.get('class') == 'act':
            # load act into memory
            act_xml = BeautifulSoup(etree.tostring(elem), 'xml')
            subacts = act_xml.find_all(act)
            # act_xml should contain exactly one act; if it contains more acts,
            # these acts are sub acts, that will be processed later
            if len(subacts) == 1:
                print 'act:', act_xml.find('div', 'act').attrs.get('xml:id')
                s_id, term_id = xml2kafnaf(act_xml, s_id, term_id, text, terms)
        elif elem.tag == entities_tag:
            emo_id = emotions2naf(emotions, markables, elem, emo_id)

    for t in emotions + markables:
        emotions_layer.append(t)

    f = os.path.join(output_dir, 'naf_test.xml')
    naf_document.write(f, xml_declaration=True, encoding='utf-8', method='xml',
                       pretty_print=True)
