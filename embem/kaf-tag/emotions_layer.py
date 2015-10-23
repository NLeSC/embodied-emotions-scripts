"""Add emotions layer to naf document.

The emotions layer is created based on FoLiA files containing embodied emotions
annotations or heem label predictions.

Usage: python emotions_layer.py <dir naf> <dir folia> <dir out>
"""
import argparse
import os
import glob
import datetime
from collections import Counter
from lxml import etree
from embem.emotools.heem_utils import heem_emotion_labels, heem_labels_en, \
    heem_modifiers_en
from folia2naf import create_linguisticProcessor

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
    etree.SubElement(emotion, 'emotion_expression')

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

    entities = [e for e in elem.findall(entity_tag) if embem_entity(e)]

    emotion_values = {}
    for ent in entities:
        ids = [wref.get('id') for wref in ent.findall(wref_tag)]
        x = ''.join(ids)
        if x not in emotion_values.keys():
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir_naf', help='directory containing NAF files')
    parser.add_argument('input_dir_folia', help='directory containing FoLiA '
                        'XML files containing annotations')
    parser.add_argument('output_dir', help='the directory where the '
                        'updated KAF files should be saved')
    args = parser.parse_args()

    input_dir_naf = args.input_dir_naf
    input_dir_folia = args.input_dir_folia

    output_dir = args.output_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    folia_files = glob.glob('{}/*.xml'.format(input_dir_folia))

    entities_tag = '{http://ilk.uvt.nl/folia}entities'

    modifiers = Counter()

    for i, f in enumerate(folia_files):
        print '{} ({} of {})'.format(f, (i + 1), len(folia_files))
        text_id = f[-20:-7]

        # Load folia document
        context = etree.iterparse(f, events=('end',), tag=(entities_tag),
                                  huge_tree=True)

        emo_id = 1

        emotions = []
        markables = []

        for event, elem in context:
            emo_id = emotions2naf(emotions, markables, elem, emo_id)

        # Load naf document
        file_name = os.path.basename(f)
        naf_file = os.path.join(input_dir_naf, file_name)
        parser = etree.XMLParser(remove_blank_text=True)
        naf = etree.parse(naf_file, parser)
        header = naf.find('nafHeader')

        # add linguistic processor to header for annotations
        ctime = str(datetime.datetime.fromtimestamp(os.path.getmtime(f)))
        create_linguisticProcessor('emotions', 'Embodied Emotions Annotations',
                                   '1.0', ctime, header)

        # add emotions layer
        emotions_layer = etree.SubElement(naf.getroot(), 'emotions')

        # add emotions and markables to emotions layer
        for t in emotions + markables:
            emotions_layer.append(t)

        # save naf document
        xml_out = os.path.join(output_dir, file_name)
        print 'writing', xml_out
        naf.write(xml_out, xml_declaration=True, encoding='utf-8',
                  method='xml', pretty_print=True)
        print
