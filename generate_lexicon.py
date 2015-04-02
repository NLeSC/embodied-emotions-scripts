"""Create multilabel data set to train embodied emotions classifiers
The data set consists of:
<sentence id>\t<sentence>\tEmotie_Liefde (embodied emotions labels separated by
_)
<sentence id>\t<sentence>\tNone ('None' if no words were tagged)

Usage: python folia2dataset_multiclass.py <file in> <output dir>
Or: ./batch_do_python.sh folia2dataset_multiclass.py <dir in> <output dir>
(for a directory containing folia files)
"""
from lxml import etree
from bs4 import BeautifulSoup
import argparse
import codecs
import os
import errno
from emotools.heem_utils import heem_concept_type_labels, heem_emotion_labels
from folia2kaf import _folia_pos2kaf_pos
import sys

time_period = '1600-1830'


def get_word_details(sentence_xml, word_id):
    words = sentence_xml.find_all('w')
    for word in words:
        w = word.get('xml:id')
        if w == word_id:
            lemma = word.find('lemma').attrs.get('class')
            pos = _folia_pos2kaf_pos.get(word.find('pos').attrs.get('head'))

            return pos.lower(), lemma
    return None, None


def lexical_entry(pos_tag, written_form, lemma, heem_tag):
    soup = BeautifulSoup(u'<LexicalEntry id="{}-{}-1" partOfSpeech="{}"'.
                         format(lemma, pos_tag, pos_tag), 'xml')
    le = soup.LexicalEntry
    lm = soup.new_tag('Lemma', writtenForm=lemma)
    le.append(lm)
    wfs = soup.new_tag('WordForms')
    le.append(wfs)
    wf = soup.new_tag('WordForm', writtenForm=written_form,
                      tense='', timePeriod=time_period)
    wfs.append(wf)
    sense = soup.new_tag('Sense', senseId=lemma, definition='')
    le.append(sense)
    sem = soup.new_tag('Semantics')
    sense.append(sem)

    add_concept_type_or_emotion_label(sem, heem_tag, soup)

    #print le.prettify()
    return le


def add_concept_type_or_emotion_label(xml, heem_tag, soup):
    if heem_tag in heem_concept_type_labels:
        concept_type_or_emotion_label = 'ConceptType'
    else:
        concept_type_or_emotion_label = 'EmotionLabel'

    lb = xml.find(concept_type_or_emotion_label, value=heem_tag)
    if not lb:
        print 'adding entry'
        tag_name = '{}s'.format(concept_type_or_emotion_label)
        lbs = xml.find('{}s'.format(concept_type_or_emotion_label))
        if not lbs:
            print 'adding parent layer'
            lbs = soup.new_tag(tag_name)
            xml.append(lbs)
        lb = soup.new_tag(concept_type_or_emotion_label, value=heem_tag,
                          internalSystem='HEEM')
        lbs.append(lb)
        #print lbs.prettify()


def add_written_form(wfs, written_form, soup):
    wf = wfs.find('WordForm', writtenForm=written_form)
    if not wf:
        print 'Adding new written form', written_form
        wf = soup.new_tag('WordForm', writtenForm=written_form,
                          tense='', timePeriod=time_period)
        wfs.append(wf)


def add_or_update_lexical_entry(soup, pos_tag, written_form, lemma, heem_tag):
    print lemma
    # does lexical entry already existi?
    # lexical entry already exist if there is an entry with matching lemma and
    # pos tag.
    lem = soup.find('Lemma', writtenForm=lemma)
    if lem and lem.parent.attrs.get('partOfSpeech') == pos_tag:
        print 'Update instead of new!'
        add_written_form(lem.parent.WordForms, written_form, soup)
        add_concept_type_or_emotion_label(lem.parent.Sense.Semantics, heem_tag,
                                          soup)
    else:
        print 'New LexicalEntry'
        le = lexical_entry(pos_tag, written_form, lemma, l[1])
        soup.LexicalResource.Lexicon.append(le)


def update_lexical_entry(entry_bs, pos_tag, written_form, lemma, heem_tag):
    """Add relevant information to existing lexical entry"""

    # wordform
    wf = entry_bs.find('WordForm', writtenForm=written_form)
    if not wf:
        wf.WordForms.new_tag('WordForm', writtenForm=written_form, tense='',
                             timePeriod='1600-1830')

    # concept type
    ct = entry_bs.find('ConceptType', value=heem_tag)
    if not ct:
        cts = entry_bs.find('ConceptTypes')
        if not cts:
            entry_bs.Sense.Semantics.new_tag('ConceptTypes')
        cts = entry_bs.find('ConceptTypes')
        etree.SubElement(cts, 'ConceptType', {'value': heem_tag,
                                              'internalSystem': 'HEEM'})
        
        
    # emotion label

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='the name of the FoLiA XML file that '
                        'should be processed.')
    parser.add_argument('lexicon', help='the directory where the '
                        'generated text files should be saved')
    args = parser.parse_args()

    input_dir = args.dir
    lexicon_file = args.lexicon

    # Does lexicon exist?
    if not os.path.isfile(lexicon_file):
        try:
            os.makedirs(os.path.dirname(lexicon_file))
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise

        root = etree.Element('LexicalResource')
        lexicon_xml = etree.ElementTree(root)
        heem_label = "Historic Embodied Emotions Model (HEEM) Lexicon"
        gi = etree.SubElement(root, 'GlobalInformation', {'label': heem_label})
        le = etree.SubElement(gi, 'Lexicon',
                              {
                                  'languageCoding': "ISO 639-2",
                                  'label': "HEEM lexicon 1.0",
                                  'language': "nl",
                                  'owner': "HEEM consortium"
                              })
        with codecs.open(lexicon_file, 'wb', 'utf-8') as f:
            lexicon_xml.write(f,
                              xml_declaration=True,
                              encoding='utf-8',
                              method='xml',
                              pretty_print=True)

    # read lexicon
    with codecs.open(lexicon_file, 'rb', 'utf-8') as f:
        lexicon_xml = BeautifulSoup(f, 'xml')

    print lexicon_xml.prettify()
    
    # We are interested in labels/classes of the following three entity types:
    entity_classes = [u'EmbodiedEmotions-Level1', u'EmbodiedEmotions-Level2',
                      u'EmbodiedEmotions-EmotionLabel']

    xml_files = [xml for xml in os.listdir(input_dir) if xml.endswith('.xml')]
    for xml in xml_files:
        in_file = os.path.join(input_dir, xml)

        sentence_tag = '{http://ilk.uvt.nl/folia}s'

        # Load document
        xml_doc = os.path.join(input_dir, xml)
        context = etree.iterparse(xml_doc, events=('end',), tag=sentence_tag)

        for event, elem in context:
            # load act into memory
            sentence = BeautifulSoup(etree.tostring(elem), 'xml')

            entities = sentence.find_all('entity')
            for entity in entities:
                e = entity.attrs.get('class')
                for cl in entity_classes:
                    if e.startswith(cl):
                        l = e.split(':')
                        wrefs = entity.find_all('wref')
                        if len(wrefs) == 1:
                            # Single word entry for lexicon
                            w_id = wrefs[0].attrs.get('id')
                            pos_tag, lemma = get_word_details(sentence, w_id)
                            written_form = wrefs[0].attrs.get('t')
                            add_or_update_lexical_entry(lexicon_xml, pos_tag,
                                                        written_form, lemma,
                                                        l[1])
                        else:
                            # multiple word entry for lexicon
                            print 'Ignoring multi-word annotation for now'
        print lexicon_xml.prettify()
        del context
        with codecs.open(lexicon_file, 'wb', 'utf-8') as f:
            f.write(lexicon_xml.prettify())
        sys.exit()
