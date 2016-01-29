"""Create a NAF file containing a terms layer from FoLiA files.
Usage: python folia2naf.py <dir in> <corpus metadata csv> <dir out>
"""
#import recipy
from lxml import etree
from bs4 import BeautifulSoup
from embem.emotools.bs4_helpers import act, sentence, word, speaker_turn, note
import argparse
import os
import glob
from collections import Counter
import pandas as pd
import datetime
import gzip
from embem.machinelearningdata.count_labels import corpus_metadata
from folia2kaf import _folia_pos2kaf_pos

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
    try:
        author = metadata.at[text_id, 4].decode('utf-8')
        etree.SubElement(header, 'fileDesc', creationtime=timestamp,
                         title=unicode(title), author=unicode(author),
                         filename=fname, filetype='FoLiA/XML')
    except:
        etree.SubElement(header, 'fileDesc', creationtime=timestamp,
                         title=unicode(title), filename=fname,
                         filetype='FoLiA/XML')


def create_public(text_id, header):
    if text_id.startswith('F'):
        etree.SubElement(header, 'public', publicId=text_id)
    else:
        uri = 'http://dbnl.nl/titels/titel.php?id={}'.format(text_id)
        etree.SubElement(header, 'public', publicId=text_id, uri=uri)


def create_linguisticProcessor(layer, lps, timestamp, header):
    lp = header.find('linguisticProcessors[@layer="{}"]'.format(layer))
    if lp is None:
        lp = etree.SubElement(header, 'linguisticProcessors', layer=layer)
    for name, version in lps.iteritems():
        etree.SubElement(lp, 'lp', name=name, version=version,
                         timestamp=timestamp)


def add_word2naf(elem, s_id, term_id, offset, text, terms):
    w_id = elem.get('xml:id')
    word = unicode(elem.t.string)
    w = etree.SubElement(text, 'wf', id=w_id, sent=s_id,
                         offset=unicode(offset), length=unicode(len(word)))
    w.text = word
    lemma = elem.lemma.get('class')
    pos = _folia_pos2kaf_pos[elem.pos.get('head', 'SPEC')]

    t_id = 't{}'.format(term_id)
    t = etree.SubElement(terms, 'term', id=t_id, type='open', lemma=lemma,
                         pos=pos)
    s = etree.SubElement(t, 'span')
    target = etree.SubElement(s, 'target', id=w_id)

    return offset + len(word) + 1


def xml2naf(xml, sentence_id, term_id, offset, text, terms):
    for elem in xml.descendants:
        if sentence(elem) and not note(elem.parent):
            sentence_id += 1
        elif word(elem) and not note(elem.parent.parent):
            offset = add_word2naf(elem, str(sentence_id), term_id, offset,
                                  text, terms)
            term_id += 1
    return sentence_id, term_id, offset


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

    if xml_files == []:
        xml_files = glob.glob('{}/*.xml.gz'.format(input_dir))

    act_tag = '{http://ilk.uvt.nl/folia}div'
    annotation_tag = '{http://ilk.uvt.nl/folia}token-annotation'
    sentence_tag = '{http://ilk.uvt.nl/folia}s'
    note_tag = '{http://ilk.uvt.nl/folia}note'

    modifiers = Counter()

    for i, fi in enumerate(xml_files):
        print '{} ({} of {})'.format(fi, (i + 1), len(xml_files))
        text_id = fi[-20:-7]

        # reset linguisting processor terms datetime
        lp_terms_datetime = ''

        ctime = datetime.datetime.fromtimestamp(os.path.getmtime(fi))
        ctime = ctime.replace(microsecond=0).isoformat()

        # create output naf xml tree
        root, naf_document, header, text, terms = create_naf()

        create_fileDesc(fi, text_id, args.metadata, ctime, header)
        create_public(text_id, header)

        # Load document
        if fi.endswith('.gz'):
            f = gzip.open(fi)
        else:
            f = fi
        context = etree.iterparse(f, events=('end',), huge_tree=True,
                                  tag=(act_tag, annotation_tag))

        s_id = 0  # in KAF, sentence numbers must be integers
        term_id = 1
        offset = 0

        found_acts = False

        for event, elem in context:
            if elem.tag == act_tag and elem.get('class') == 'act':
                found_acts = True
                # load act into memory
                act_xml = BeautifulSoup(etree.tostring(elem), 'xml')
                subacts = act_xml.find_all(act)
                # act_xml should contain exactly one act; if it contains more
                # acts, these acts are sub acts, that will be processed later
                if len(subacts) == 1:
                    print 'act:', act_xml.find('div', 'act').attrs.\
                          get('xml:id')
                    s_id, term_id, offset = xml2naf(act_xml, s_id, term_id,
                                                    offset, text, terms)
            elif elem.tag == annotation_tag:
                lp_terms_datetime = elem.attrib.get('datetime')

        if not found_acts:
            del context

            print 'Extracting sentences from s-tags'
            if fi.endswith('.gz'):
                f.close()
                f = gzip.open(fi)

            context = etree.iterparse(f, events=('end',), tag=sentence_tag,
                                      huge_tree=True)

            for event, elem in context:
                if not elem.getparent().tag == note_tag:
                    s_xml = BeautifulSoup(etree.tostring(elem), 'xml')
                    s_id, term_id, offset = xml2naf(s_xml, s_id, term_id,
                                                    offset, text, terms)
        # linguistic processors for terms
        generator = context.root.attrib.get('generator')
        name, version = generator.split('-')

        lps = {}
        lps[name] = version
        create_linguisticProcessor('terms', lps, lp_terms_datetime,
                                   header)

        # save naf document
        out_file = os.path.basename(fi)
        if out_file.endswith('.gz'):
            out_file = out_file.replace('.gz', '')
        xml_out = os.path.join(output_dir, out_file)
        print 'writing', xml_out
        naf_document.write(xml_out, xml_declaration=True, encoding='utf-8',
                           method='xml', pretty_print=True)
        print
