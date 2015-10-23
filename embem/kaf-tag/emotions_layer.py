"""Add emotions layer to naf document.

The emotions layer is created based on FoLiA files containing embodied emotions
annotations or heem label predictions.

Usage: python emotions_layer.py <dir naf> -f <dir folia> <dir out>
Or: python emotions_layer.py <dir naf> <dir out> -c <classifier>
    -d <hist2modern json>
"""
import argparse
import os
import glob
import datetime
import multiprocessing
import string
import unicodedata
from collections import Counter
from lxml import etree
from embem.emotools.heem_utils import heem_emotion_labels, heem_labels_en, \
    heem_modifiers_en, heem_concept_type_labels
from embem.machinelearning.mlutils import get_data, load_data
from embem.spellingnormalization.normalize_dataset import normalize_spelling, \
    get_hist2modern
from folia2naf import create_linguisticProcessor
from sklearn.externals import joblib

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
    for i, label in enumerate(data['labels']):
        parts = label.split(':')
        if len(parts) > 1:
            l = label.split(':')[1]
        else:
            l = label

        if l == 'Lichaamsdeel':
            l = heem_labels_en['Lichaamsdeel']
            l = lowerc(l)
            r = 'embemo:conceptType'
        elif l in heem_emotion_labels:
            l = heem_labels_en[l]
            l = lowerc(l)
            r = 'embemo:emotionType'
        else:
            parts = l.split('-')
            if len(parts) > 1:
                l = parts[1]
            else:
                l = None
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
            if data.get('confidence'):
                conf = data.get('confidence')[i]
            else:
                # TODO: decide on confidence for annotations
                conf = 1.0
            add_emoVal(markable, l, r, str(conf))
    return markable


def naf_emotion(data, emo_id):
    eid = 'emo{}'.format(emo_id)
    emotion = etree.Element('emotion', id=str(eid))
    etree.SubElement(emotion, 'emotion_target')
    etree.SubElement(emotion, 'emotion_holder')
    etree.SubElement(emotion, 'emotion_expression')

    add_targets(emotion, data['words'], data['wids'])

    # emovals
    for i, label in enumerate(data['labels']):
        parts = label.split(':')
        if len(parts) > 1:
            l = label.split(':')[1]
        else:
            l = label
        l = heem_labels_en.get(l)
        if l and l != 'BodyPart':
            l = lowerc(l)
            if l in heem_emotion_labels:
                r = 'embemo:emotionType'
            else:
                r = 'embemo:conceptType'
            if data.get('confidence'):
                confidence = data['confidence'][i]
            else:
                # TODO: decide on confidence for annotations
                confidence = 1.0
            add_emoVal(emotion, l, r, str(confidence))
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


def update_naf(file_name, timestamp, emotions, markables):
    naf, header = load_naf(file_name)

    # add linguistic processor to header for annotations
    create_linguisticProcessor('emotions', 'Embodied Emotions Annotations',
                               '1.0', timestamp, header)

    # add emotions layer
    emotions_layer = etree.SubElement(naf.getroot(), 'emotions')

    # add emotions and markables to emotions layer
    for t in emotions + markables:
        emotions_layer.append(t)

    return naf


def save_naf(naf, file_name):
    print 'writing', file_name
    naf.write(file_name, xml_declaration=True, encoding='utf-8',
              method='xml', pretty_print=True)
    print


def process_naf(f, input_dir_naf, emotions, markables, output_dir):
    file_name = os.path.basename(f)
    naf_file = os.path.join(input_dir_naf, file_name)
    ctime = str(datetime.datetime.fromtimestamp(os.path.getmtime(f)))

    naf = update_naf(naf_file, ctime, emotions, markables)

    xml_out = os.path.join(output_dir, file_name)
    save_naf(naf, xml_out)


def load_naf(file_name):
    parser = etree.XMLParser(remove_blank_text=True)
    naf = etree.parse(file_name, parser)
    header = naf.find('nafHeader')
    return naf, header


def sp_norm_word(word, hist2modern):
    if word in string.punctuation:
        return ''
    w = hist2modern.get(word, word)
    # replace accented characters by unaccented ones
    s = unicodedata.normalize('NFKD', w).encode('ascii', 'ignore')
    return s


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('naf', help='directory containing NAF files')
    parser.add_argument('output_dir', help='the directory where the '
                        'updated KAF files should be saved')
    parser.add_argument('-f', '--folia', help='directory containing FoLiA '
                        'XML files containing annotations')
    parser.add_argument('-d', '--hist2modern', help='json file containing '
                        'historic2modern mapping (json object)')
    parser.add_argument('-c', '--classifier', help='classifier file')
    args = parser.parse_args()

    input_dir_naf = args.naf

    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if args.folia:
        input_dir_folia = args.folia

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

            process_naf(f, input_dir_naf, emotions, markables, output_dir)
    elif args.hist2modern and args.classifier:
        hist2modern = get_hist2modern(args.hist2modern)

        clf = joblib.load(args.classifier)

        labels = heem_emotion_labels + heem_concept_type_labels
        labels.sort()

        naf_files = glob.glob('{}/*.xml'.format(input_dir_naf))
        for i, f in enumerate(naf_files):
            print '{} ({} of {})'.format(f, (i + 1), len(naf_files))

            # extract sentences for prediction
            sentence_id = 1
            text = []
            text_n = []
            spans = []

            words = []
            words_n = []
            word_ids = []

            naf, header = load_naf(f)

            wfs = naf.findall('.//wf')
            #print len(wfs)
            for wf in wfs:
                s_id = int(wf.attrib.get('sent'))
                if s_id != sentence_id:
                    text_n.append(unicode(' '.join(words_n)))
                    text.append(unicode(' '.join(words)))
                    spans.append(word_ids)

                    words = []
                    words_n = []
                    word_ids = []
                    sentence_id += 1
                else:
                    words_n.append(sp_norm_word(unicode(wf.text), hist2modern))
                    words.append(wf.text)
                    word_ids.append(wf.attrib.get('wid'))
            # add last sentence
            text_n.append(unicode(' '.join(words_n)))
            text.append(unicode(' '.join(words)))
            spans.append(word_ids)

            proba = clf.predict_proba(text_n)

            emotions = []
            markables = []
            emo_id = 0

            emotion_values = {}
            for i, pred in enumerate(proba):
                for j, conf in enumerate(pred):
                    if conf > 0.0:
                        x = ''.join(spans[i])
                        if x not in emotion_values.keys():
                            emotion_values[x] = {'labels': [],
                                                 'wids': spans[i],
                                                 'words': text[i].split(),
                                                 'confidence': []}
                        emotion_values[x]['labels'].append(labels[j])
                        emotion_values[x]['confidence'].append(conf)

                        #print text[i]
                        #print spans[i]
                        #print labels[j]
                        #print conf

            for key, data in emotion_values.iteritems():
                emotion, emo_id = naf_emotion(data, emo_id)
                if emotion is not None:
                    emotions.append(emotion)
                for l in data['labels']:
                    if l in markables_labels:
                        markables.append(naf_markable(data))

            process_naf(f, input_dir_naf, emotions, markables, output_dir)

    else:
        print 'Please specify either a directory containing FoLiA files or' + \
              ' a hist2modern json file and a classifier file.'
