"""Add heem clusters and heem posneg to naf document.

The script adds emoVals for all emotion labels based on a mapping specified
in a json object.

Usage: python add_emoclusters.py <dir naf> <dir out> <replacements json> <name>
"""
import argparse
import json
import codecs
import os
import glob
from lxml import etree
from embem.emotools.heem_utils import heem_emotion_labels, heem_labels_en, \
    heem_modifiers_en, heem_concept_type_labels
from emotions_layer import load_naf, lowerc, add_emoVal, save_naf


def add_emovals(elements, en2nl, replacements, name):
    for elem in elements:
        transf = {}
        emoVals = elem.findall('emoVal')
        for emoVal in emoVals:
            emNL = en2nl.get(emoVal.attrib.get('value'))
            #print emNL
            if emNL in heem_emotion_labels:
                for cat, lbls in replacements.iteritems():
                    if emNL in lbls:
                        if not cat in transf:
                            transf[cat] = []
                        if emoVal.attrib.get('confidence'):
                            transf[cat].append(emoVal.attrib.get('confidence'))
        for cat, conf in transf.iteritems():
            add_emoVal(elem, lowerc(cat), 'heem:{}'.format(name),
                       str(max(conf)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('naf', help='directory containing NAF files')
    parser.add_argument('output_dir', help='the directory where the '
                        'updated KAF files should be saved')
    parser.add_argument('replacements', help='json file containing label '
                        'replacements')
    parser.add_argument('name', help='resource name (e.g., clusters or '
                        'posNeg)')
    args = parser.parse_args()

    input_dir_naf = args.naf

    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print 'loading label replacements from {}'.format(args.replacements)
    with codecs.open(args.replacements, 'rb', 'utf8') as f:
        replacements = json.load(f, encoding='utf8')

    en2nl = {}
    for nl, en in heem_labels_en.iteritems():
        en2nl[lowerc(en)] = nl
    print en2nl

    naf_files = glob.glob('{}/*.xml'.format(input_dir_naf))
    for i, f in enumerate(naf_files):
        print '{} ({} of {})'.format(f, (i + 1), len(naf_files))

        naf, header = load_naf(f)

        emotions = naf.findall('.//emotion')
        add_emovals(emotions, en2nl, replacements, args.name)

        markables = naf.findall('.//markable')
        add_emovals(markables, en2nl, replacements, args.name)

        # save naf document
        out_file = os.path.basename(f)
        xml_out = os.path.join(output_dir, out_file)
        save_naf(naf, xml_out)
