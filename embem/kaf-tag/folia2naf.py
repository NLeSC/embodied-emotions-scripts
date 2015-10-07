"""Create a KAF file for each act in a FoLiA file
Usage: python folia2kaf.py <file in> <output dir>
Or: ./generate_kaf.sh <dir in> <dir out>
"""
from lxml import etree
from bs4 import BeautifulSoup
from embem.emotools.bs4_helpers import act, sentence, word, speaker_turn, note
from folia2kaf import xml2kafnaf
import argparse
import os


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

    # Load document
    context = etree.iterparse(file_name, events=('end',), tag=act_tag)

    act_number = 0

    s_id = 0  # in KAF, sentence numbers must be integers
    term_id = 1
    w_id = None

    # create output naf xml tree for act
    root = etree.Element('NAF')
    naf_document = etree.ElementTree(root)
    text = etree.SubElement(root, 'text')
    terms = etree.SubElement(root, 'terms')

    # TODO: nafheader with fileDesc and linguistic processors

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

    f = os.path.join(output_dir, 'naf_test.xml')
    naf_document.write(f, xml_declaration=True, encoding='utf-8', method='xml',
                       pretty_print=True)
