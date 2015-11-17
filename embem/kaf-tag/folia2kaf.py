"""Create a KAF file for each act in a FoLiA file
Usage: python folia2kaf.py <file in> <output dir>
Or: ./generate_kaf.sh <dir in> <dir out>
"""
from lxml import etree
from bs4 import BeautifulSoup
from embem.emotools.bs4_helpers import act, sentence, word, speaker_turn, note
import argparse
import os


_folia_pos2kaf_pos = {
    'WW': 'V',   # Werkwoord -> Verb
    'VNW': 'Q',  # Voornaamwoord -> Pronoun
    'VZ': 'P',   # Voorzetsel -> Preposition
    'LID': 'D',  # Lidwoord -> Determiner
    'N': 'N',    # Zelfstandig naamwoord -> Common noun
    'VG': 'C',   # Voegwoord -> Conjunction
    'TW': 'O',   # Interjection (?) -> Other
    'BW': 'A',   # Bijwoord -> Adverb
    'LET': 'O',  # Interpunctie -> Other
    'TSW': 'O',  # Ja/nee(?) -> Other
    'ADJ': 'G',  # Bijvoegelijk naamwoord -> Adjective
    'SPEC': 'O'  # Special (niet nader gespecificeerd) -> Other
    # Geen folia_pos voor Proper Noun (R)
}


def kaf_file_name(input_file, act_number):
    head, tail = os.path.split(input_file)
    p = tail.split('.')
    return '{n}__act-0{a}.kaf'.format(a=act_number, n=p[0])


def add_word2kaf(elem, s_id, term_id, text, terms):
    w_id = elem.get('xml:id')
    w = etree.SubElement(text, 'wf', wid=w_id, sent=s_id)
    w.text = unicode(elem.t.string)
    lemma = elem.lemma.get('class')
    pos = _folia_pos2kaf_pos[elem.pos.get('head', 'SPEC')]

    t_id = 't{wid}'.format(wid=term_id)
    t = etree.SubElement(terms, 'term', tid=t_id, type='open', lemma=lemma,
                         pos=pos)
    s = etree.SubElement(t, 'span')
    target = etree.SubElement(s, 'target', id=w_id)


def act2kaf(act_xml, sentence_id):
    """Convert act to kaf xml. Returns an XML tree that can be written to file.
    """
    print 'act:', act_xml.find('div', 'act').attrs.get('xml:id')

    kaf_document = None
    subacts = act_xml.find_all(act)

    # act_xml should contain exactly one act; if it contains more acts, these
    # acts are sub acts, that will be processed later
    if len(subacts) == 1:
        term_id = 1

        # create output kaf xml tree for act
        root = etree.Element('KAF')
        kaf_document = etree.ElementTree(root)
        text = etree.SubElement(root, 'text')
        terms = etree.SubElement(root, 'terms')

        sentence_id, term_id = xml2kaf(act_xml, sentence_id, term_id, text,
                                       terms)

    return kaf_document, sentence_id


def xml2kaf(xml, sentence_id, term_id, text, terms):
    for elem in xml.descendants:
        if sentence(elem) and not note(elem.parent):
            sentence_id += 1
        elif word(elem) and not note(elem.parent.parent):
            add_word2kaf(elem, str(sentence_id), term_id, text, terms)
            term_id += 1
    return sentence_id, term_id


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='the name of the FoLiA XML file to '
                        'generate KAF files for')
    parser.add_argument('output_dir', help='the directory where the '
                        'generated KAF files should be saved')
    args = parser.parse_args()

    file_name = args.file
    output_dir = args.output_dir

    act_tag = '{http://ilk.uvt.nl/folia}div'

    # Load document
    context = etree.iterparse(file_name, events=('end',), tag=act_tag)

    act_number = 0

    s_id = 0  # in KAF, sentence numbers must be integers
    w_id = None

    for event, elem in context:
        if elem.tag == act_tag and elem.get('class') == 'act':
            # load act into memory
            act_xml = BeautifulSoup(etree.tostring(elem), 'xml')
            kaf_document, s_id = act2kaf(act_xml, s_id)

            if kaf_document:
                act_number += 1

                # write kaf xml tree to file
                kaf_file = '{}{}{}'.format(output_dir, os.sep,
                                           kaf_file_name(file_name,
                                                         act_number))
                print kaf_file
                with open(kaf_file, 'w') as f:
                    kaf_document.write(f,
                                       xml_declaration=True,
                                       encoding='utf-8',
                                       method='xml',
                                       pretty_print=True)
