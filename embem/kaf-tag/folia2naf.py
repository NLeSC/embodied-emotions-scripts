"""Create a NAF file containing a terms layer from FoLiA files.
Usage: python folia2naf.py <dir in> <corpus metadata csv> <dir out>
"""
from lxml import etree
from bs4 import BeautifulSoup
from embem.emotools.bs4_helpers import act
from folia2kaf import xml2kafnaf
import argparse
import os
import glob
from collections import Counter
import pandas as pd
import datetime
from embem.machinelearningdata.count_labels import corpus_metadata

genres_en = {'blijspel / komedie': 'comedy',
             'tragedie/treurspel': 'tragedy',
             'klucht': 'farce',
             'Anders': 'other',
             'unknown': 'unknown'}


def create_naf():
    root = etree.Element('NAF', lang='nl', version='v4')
    naf_document = etree.ElementTree(root)
    header = etree.SubElement(root, 'nafHeader')
    text = etree.SubElement(root, 'text')
    terms = etree.SubElement(root, 'terms')

    return root, naf_document, header, text, terms


def create_fileDesc(xml_file, text_id, metadata_file, timestamp, header):
    fname = os.path.basename(xml_file)

    text2period, text2year, text2genre, period2text, genre2text = \
        corpus_metadata(metadata_file)
    year = text2year[text_id]
    genre = genres_en.get(text2genre[text_id], 'unknown')
    metadata = pd.read_csv(metadata_file, header=None, sep='\\t', index_col=0,
                           encoding='utf-8', engine='python')
    title = metadata.at[text_id, 3].decode('utf-8')
    author = metadata.at[text_id, 4].decode('utf-8')
    etree.SubElement(header, 'fileDesc', creationtime=timestamp,
                     title=unicode(title), author=unicode(author),
                     filename=fname, filetype='FoLiA/XML', year=year,
                     genre=genre)


def create_public(text_id, header):
    uri = 'http://dbnl.nl/titels/titel.php?id={}'.format(text_id)
    etree.SubElement(header, 'public', publicId=text_id, uri=uri)


def create_linguisticProcessor(layer, name, version, timestamp, header):
    lp = etree.SubElement(header, 'linguisticProcessors', layer=layer)
    etree.SubElement(lp, 'lp', name=name, version=version, timestamp=timestamp)


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
    annotation_tag = '{http://ilk.uvt.nl/folia}token-annotation'

    modifiers = Counter()

    for i, f in enumerate(xml_files):
        print '{} ({} of {})'.format(f, (i + 1), len(xml_files))
        text_id = f[-20:-7]

        # reset linguisting processor terms datetime
        lp_terms_datetime = ''

        # Load document
        context = etree.iterparse(f, events=('end',), huge_tree=True,
                                  tag=(act_tag, annotation_tag))

        s_id = 0  # in KAF, sentence numbers must be integers
        term_id = 1
        emo_id = 1

        # create output naf xml tree
        root, naf_document, header, text, terms = create_naf()

        ctime = str(datetime.datetime.fromtimestamp(os.path.getmtime(f)))

        create_fileDesc(f, text_id, args.metadata, ctime, header)
        create_public(text_id, header)

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
            elif elem.tag == annotation_tag:
                lp_terms_datetime = elem.attrib.get('datetime')

        # linguistic processors for terms
        generator = context.root.attrib.get('generator')
        name, version = generator.split('-')
        create_linguisticProcessor('terms', name, version, lp_terms_datetime,
                                   header)

        # save naf document
        out_file = os.path.basename(f)
        xml_out = os.path.join(output_dir, out_file)
        print 'writing', xml_out
        naf_document.write(xml_out, xml_declaration=True, encoding='utf-8',
                           method='xml', pretty_print=True)
        print
