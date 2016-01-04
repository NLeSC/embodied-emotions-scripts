"""Add emotions layer to naf document.

The emotions layer is created based on FoLiA files containing embodied emotions
annotations or heem label predictions.

Usage: python emotions_layer.py <dir naf> <dir out> -f <dir folia>
[-b <body part mapping>]

Or: python emotions_layer.py <dir naf> <dir out> -c <classifier>
    -d <hist2modern json> [-b <body part mapping>]

If <body part mapping> is specified, body parts are expanded.
"""
import argparse
import os
import glob
from datetime import datetime
import multiprocessing
import string
import unicodedata
import re
from collections import Counter
from lxml import etree
from embem.emotools.heem_utils import heem_emotion_labels, heem_labels_en, \
    heem_modifiers_en, heem_concept_type_labels, \
    heem_humor_modifier_labels, heem_intensifier_labels
from embem.machinelearning.mlutils import get_data, load_data
from embem.spellingnormalization.normalize_dataset import normalize_spelling, \
    get_hist2modern
from embem.bodyparts.classify_body_parts import get_extended_body_part_mapping
from folia2naf import create_linguisticProcessor
from sklearn.externals import joblib

emotions_labels = ['Emotie', 'Lichaamswerking', 'EmotioneleHandeling',
                   'Lichaamsdeel', 'HumorModifier', 'Intensifier']


def embem_entity(elem):
    if elem.get('class').startswith('EmbodiedEmotions'):
        return True
    return False


def contains_emotion(entities):
    labels = [ent.get('class').split(':')[1] for ent in entities]

    #if bool(set(labels) & set(emotions_labels)):
        #print 'Emotion!'

    return bool(set(labels) & set(emotions_labels))


def lowerc(string):
    """Lowercase first character of input string"""
    return string[0].lower() + string[1:]


def add_targets(elem, words, ids):
    span = etree.SubElement(elem, 'span')
    # Add words as comment (with dashes (-) removed, because xml doesn't like
    # dashes in comments)
    comment = re.sub(r'-+', '', ' '.join(words))
    span.append(etree.Comment(' ' + comment + ' '))
    # word ids (targets)
    for i in ids:
        etree.SubElement(span, 'target', id=i)


def add_external_reference(elem, resource, reference, confidence):
    """
    Parameters:
    elem : etree.SubElement (emotion)
    resource : string (i.e., 'heem')
    reference : Dutch embodied emotions label or correctly formatted label
    confidence : float or None
    """
    if reference in heem_emotion_labels:
        reference = 'emotionType:{}'.format(lowerc(heem_labels_en.get(reference)))
    elif reference in heem_concept_type_labels:
        reference = 'conceptType:{}'.format(lowerc(heem_labels_en.get(reference)))
    elif reference in heem_intensifier_labels:
        reference = 'intensifier:{}'.format(lowerc(heem_modifiers_en.get(reference)))
    elif reference in heem_humor_modifier_labels:
        reference = 'humorModifier:{}'.format(lowerc(heem_modifiers_en.get(reference)))

    ext_refs = elem.find('externalReferences')
    if ext_refs is None:
        ext_refs = etree.SubElement(elem, 'externalReferences')

    if confidence:
        etree.SubElement(ext_refs, 'externalRef', resource=resource,
                         reference=reference, confidence=confidence)
    else:
        etree.SubElement(ext_refs, 'externalRef', resource=resource,
                         reference=reference)


def naf_emotion(data, emo_id, bpmapping=None):
    eid = 'emo{}'.format(emo_id)
    emotion = etree.Element('emotion', id=str(eid))
    etree.SubElement(emotion, 'emotion_target')
    etree.SubElement(emotion, 'emotion_holder')
    etree.SubElement(emotion, 'emotion_expression')

    add_targets(emotion, data['words'], data['tids'])

    # emovals
    for i, label in enumerate(data['labels']):
        l = label
        if label not in heem_emotion_labels + heem_concept_type_labels + \
                heem_intensifier_labels + heem_humor_modifier_labels:
            l = None

        if l:
            if data.get('confidence'):
                confidence = str(data['confidence'][i])
                r = 'heem'
            else:
                # TODO: decide on confidence for annotations
                confidence = None
                r = 'heem'
            add_external_reference(emotion, r, l, confidence)

            # expand body parts
            if bpmapping is not None and l == 'Lichaamsdeel':
                for w in data['words']:
                    if w in bpmapping.keys():
                        l = bpmapping.get(w)
                        r = 'heem:bodyParts'
                        add_external_reference(emotion, r, l, confidence)
    if not l:
        emotion = None
    if l:
        emo_id += 1

    return emotion, emo_id


def get_second_part(annotation):
    """Extract the label from heem annotations in folia.

    For example: from "EmbodiedEmotions-EmotionLabel:Woede" to "Woede"

    Also returns correct values for intensifiers and humor modifiers.
    """
    parts = annotation.split(':')
    if len(parts) > 1:
        return parts[1]
    return annotation


def emotions2naf(emotions, elem, emo_id, wf2term, bpmapping=None):
    entity_tag = '{http://ilk.uvt.nl/folia}entity'
    wref_tag = '{http://ilk.uvt.nl/folia}wref'

    entities = [e for e in elem.findall(entity_tag) if embem_entity(e)]

    emotion_values = {}
    for ent in entities:
        ids = [wref.get('id') for wref in ent.findall(wref_tag)]
        tids = [wf2term.get(wid) for wid in ids]
        x = ''.join(ids)
        if x not in emotion_values.keys():
            words = [wref.get('t') for wref in ent.findall(wref_tag)]
            emotion_values[x] = {'labels': [], 'wids': ids, 'words': words,
                                 'entities': [], 'tids': tids}
        label = get_second_part(ent.get('class'))
        emotion_values[x]['labels'].append(label)
        emotion_values[x]['entities'].append(ent)

    for key, data in emotion_values.iteritems():
        if contains_emotion(data['entities']):
            # Add entity as emotion if it contains an emotion.
            # The data set contains words tagged with only an emotion label
            # These annotations are also added as emotion
            #print 'Add emotion!'
            #print [(e.tag, e.attrib) for e in data['entities']]
            emotion, emo_id = naf_emotion(data, emo_id, bpmapping)
            if emotion is not None:
                emotions.append(emotion)

    return emo_id


def update_naf(file_name, timestamp, emotions, lps):
    layer_name = 'emotions'
    naf, header = load_naf(file_name)

    # add linguistic processor to header for annotations
    create_linguisticProcessor(layer_name, lps, timestamp, header)

    # add emotions layer
    emotions_layer = etree.SubElement(naf.getroot(), layer_name)

    # add emotions to emotions layer
    for t in emotions:
        emotions_layer.append(t)

    return naf


def save_naf(naf, file_name):
    print 'writing', file_name
    naf.write(file_name, xml_declaration=True, encoding='utf-8',
              method='xml', pretty_print=True)
    print


def process_naf(f, input_dir_naf, emotions, output_dir, lps):
    file_name = os.path.basename(f)
    naf_file = os.path.join(input_dir_naf, file_name)
    ctime = datetime.fromtimestamp(os.path.getmtime(f))
    ctime = ctime.replace(microsecond=0).isoformat()

    naf = update_naf(naf_file, ctime, emotions, lps)

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


def create_wf2term_mapping(naf):
    terms = naf.findall('.//term')

    mapping = {}
    for t in terms:
        tid = t.attrib.get('id')
        wid = t.find('.//target').attrib.get('id')
        mapping[wid] = tid
    return mapping


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
    parser.add_argument('-b', '--bpmapping', help='json file containing '
                        'extend body part mapping (json object)')
    args = parser.parse_args()

    input_dir_naf = args.naf

    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    bpmapping = None
    if args.bpmapping:
        print 'loading body part mapping from {}'.format(args.bpmapping)
        bpmapping = get_extended_body_part_mapping(args.bpmapping)
        print

    if args.folia:
        input_dir_folia = args.folia

        folia_files = glob.glob('{}/*.xml'.format(input_dir_folia))

        entities_tag = '{http://ilk.uvt.nl/folia}entities'

        modifiers = Counter()

        for i, f in enumerate(folia_files):
            print '{} ({} of {})'.format(f, (i + 1), len(folia_files))
            text_id = f[-20:-7]

            file_name = os.path.basename(f)
            naf_file = os.path.join(input_dir_naf, file_name)
            naf, header = load_naf(naf_file)
            wf2term = create_wf2term_mapping(naf)

            # Load folia document
            context = etree.iterparse(f, events=('end',), tag=(entities_tag),
                                      huge_tree=True)

            emo_id = 0
            emotions = []

            for event, elem in context:
                emo_id = emotions2naf(emotions, elem, emo_id, wf2term,
                                      bpmapping)

            lps = {'Embodied Emotions Manual Annotations': '1.0'}
            if args.bpmapping:
                lps['heem-expand-body_parts'] = '1.0'
            #print lps
            process_naf(f, input_dir_naf, emotions, output_dir, lps)
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
            wf2term = create_wf2term_mapping(naf)

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
                    word_ids.append(wf.attrib.get('id'))
            # add last sentence
            text_n.append(unicode(' '.join(words_n)))
            text.append(unicode(' '.join(words)))
            spans.append(word_ids)

            proba = clf.predict_proba(text_n)

            emotions = []
            emo_id = 0

            emotion_values = {}
            for i, pred in enumerate(proba):
                for j, conf in enumerate(pred):
                    if conf > 0.0:
                        x = ''.join(spans[i])
                        if x not in emotion_values.keys():
                            tids = [wf2term.get(wid) for wid in spans[i]]
                            emotion_values[x] = {'labels': [],
                                                 'wids': spans[i],
                                                 'tids': tids,
                                                 'words': text[i].split(),
                                                 'confidence': []}
                        emotion_values[x]['labels'].append(labels[j])
                        emotion_values[x]['confidence'].append(conf)

                        #print text[i]
                        #print spans[i]
                        #print labels[j]
                        #print conf

            for key, data in emotion_values.iteritems():
                emotion, emo_id = naf_emotion(data, emo_id, bpmapping)
                if emotion is not None:
                    emotions.append(emotion)

            lps = {'rakel-heem-spelling_normalized': '1.0'}
            if args.bpmapping:
                lps['heem-expand-body_parts'] = '1.0'
            #print lps
            process_naf(f, input_dir_naf, emotions, output_dir, lps)
    else:
        print 'Please specify either a directory containing FoLiA files or' + \
              ' a hist2modern json file and a classifier file.'
