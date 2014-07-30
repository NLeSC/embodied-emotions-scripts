"""Create a KAF file for each act in a FoLiA file
Usage: python folia2kaf.py <file in>
"""
from lxml import etree
from bs4 import BeautifulSoup
from emotools.bs4_helpers import act, sentence, word, speaker_turn, note
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
    return '{h}{s}{n}__act-0{a}.kaf'.format(a=act_number, 
                                            n=p[0], 
                                            h=head, 
                                            s=os.sep)


def add_word2kaf(elem, w_id, s_id, term_id, text, terms):
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='the name of the FoLiA XML file to ' \
                        'generate KAF files for')
    args = parser.parse_args()

    file_name = args.file

    # Load document
    #doc = folia.Document(file='medea-folia-no_events.xml')
    with open(file_name, 'r') as f:
        soup = BeautifulSoup(f, 'xml')

    acts = soup.find_all(act)

    act_number = 0
    
    s_id = 0  # in KAF, sentence numbers must be integers
    w_id = None

    for a in acts:
        print 'act:', a.get('xml:id')
        subacts = a.find_all(act)
        if not subacts:
            act_number += 1
            term_id = 1

            # create output kaf xml tree for act
            root = etree.Element('KAF')
            kaf_document = etree.ElementTree(root)
            text = etree.SubElement(root, 'text')
            terms = etree.SubElement(root, 'terms')

            for elem in a.descendants:
                if sentence(elem) and not note(elem.parent):
                    s_id += 1
                elif word(elem) and not note(elem.parent.parent):
                    add_word2kaf(elem, w_id, str(s_id), term_id, text, terms)

                    term_id += 1
            
            # write kaf xml tree to file
            kaf_file = kaf_file_name(file_name, act_number)
            print kaf_file
            with open(kaf_file, 'w') as f:
                kaf_document.write(f, xml_declaration=True, encoding='utf-8', method='xml', pretty_print=True)
