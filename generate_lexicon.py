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
from emotools.heem_utils import heem_concept_type_labels, heem_labels_en
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


def add_lexical_entry(soup, pos_tag, written_form, lemma, heem_tag):
    le = soup.new_tag('LexicalEntry', id=u'{}-{}'.format(lemma, pos_tag),
                      partOfSpeech=pos_tag)
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
    add_heem_classification(soup, heem_tag)
    soup.LexicalResource.GlobalInformation.Lexicon.append(le)


def add_lexical_entry_mwe(soup, word_list, heem_tag):
    mwe_id = u'_'.join(word_list)
    written_form = unicode(' '.join(word_list))
    le = soup.new_tag('LexicalEntry', id=u'{}-mwe'.format(mwe_id))
    mwe = soup.new_tag('MultiWordExpression', writtenForm=written_form)
    le.append(mwe)

    sense = soup.new_tag('Sense', senseId=mwe_id, definition='')
    le.append(sense)
    sem = soup.new_tag('Semantics')
    sense.append(sem)

    add_concept_type_or_emotion_label(sem, heem_tag, soup)
    add_heem_classification(soup, heem_tag)
    soup.LexicalResource.GlobalInformation.Lexicon.append(le)


def get_label_type(heem_tag):
    if heem_tag in heem_concept_type_labels:
        concept_type_or_emotion_label = 'ConceptType'
    else:
        concept_type_or_emotion_label = 'EmotionLabel'
    return concept_type_or_emotion_label


def add_concept_type_or_emotion_label(xml, heem_tag, soup):
    concept_type_or_emotion_label = get_label_type(heem_tag)
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
        return lb


def add_heem_classification(soup, heem_tag, internalSystem='HEEM'):
    label_type = get_label_type(heem_tag)
    label_en = heem_labels_en.get(heem_tag)
    print label_type
    cl = soup.LexicalResource.GlobalInformation.HeemClassification. \
        find(label_type, id=label_en)
    if not cl:
        heem_label = soup.new_tag(label_type, id=label_en)
        heem_label.append(soup.new_tag('Class', value=heem_tag,
                                       internalSystem=internalSystem))
        soup.LexicalResource.GlobalInformation.HeemClassification.append(heem_label)


def add_written_form(wfs, written_form, soup):
    wf = wfs.find('WordForm', writtenForm=written_form)
    if not wf:
        print 'Adding new written form', written_form
        wf = soup.new_tag('WordForm', writtenForm=written_form,
                          tense='', timePeriod=time_period)
        wfs.append(wf)


def add_or_update_lexical_entry(soup, pos_tag, written_form, lemma, heem_tag):
    print lemma, pos_tag, written_form
    # does lexical entry already existi?
    # lexical entry already exist if there is an entry with matching lemma and
    # pos tag.
    lemmas = soup.find_all('Lemma', writtenForm=lemma)
    lem = None
    for lm in lemmas:
        lemma_pos_tag = lm.parent.attrs.get('partOfSpeech')
        if pos_tag == lemma_pos_tag:
            lem = lm

    if lem:
        print 'Update instead of new!'
        add_written_form(lem.parent.WordForms, written_form, soup)
        add_concept_type_or_emotion_label(lem.parent.Sense.Semantics, heem_tag,
                                          soup)
        add_heem_classification(soup, heem_tag)
    else:
        print 'New LexicalEntry'
        add_lexical_entry(soup, pos_tag, written_form, lemma, heem_tag)
        add_heem_classification(soup, heem_tag)


def add_or_update_lexical_entry_mwe(soup, word_list, heem_tag):
    print ' '.join(word_list)
    # does lexical entry already exists?
    # lexical entry already exist if there is an entry with matching lemma and
    # pos tag.
    mwe_id = u'_'.join(word_list).encode('utf8')
    le = soup.find('LexicalEntry', id='{}-mwe'.format(mwe_id))
    if le:
        print 'Update mwe instead of new!'
        add_concept_type_or_emotion_label(le.Sense.Semantics, heem_tag, soup)
        add_heem_classification(soup, heem_tag)
    else:
        print 'New LexicalEntry for mwe'
        add_lexical_entry_mwe(soup, word_list, heem_tag)
        add_heem_classification(soup, heem_tag)


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
        hc = etree.SubElement(gi, 'HeemClassification')
        with codecs.open(lexicon_file, 'wb', 'utf-8') as f:
            lexicon_xml.write(f,
                              xml_declaration=True,
                              encoding='utf-8',
                              method='xml',
                              pretty_print=True)

    # read lexicon
    with codecs.open(lexicon_file, 'rb', 'utf-8') as f:
        lexicon_xml = BeautifulSoup(f, 'xml')

    #print lexicon_xml.prettify()

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
                        elif len(wrefs) > 1:
                            # multiple word entry for lexicon
                            words = [w.attrs.get('t') for w in wrefs]
                            add_or_update_lexical_entry_mwe(lexicon_xml, words,
                                                            l[1])
        #print lexicon_xml.prettify()
        del context
        with codecs.open(lexicon_file, 'wb', 'utf-8') as f:
            f.write(lexicon_xml.prettify())
        sys.exit()
