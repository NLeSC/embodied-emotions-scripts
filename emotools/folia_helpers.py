"""Helper functions for using the FoLiA format from pynlpl. 
"""
from pynlpl.formats import folia
from lxml import etree
import os


def parse_document(file_name):
    try:
        doc = folia.Document(file=file_name)
    except Exception as e:
        return None, 'Unable to parse FoLiA XML file.\n{}'.format(str(e))
    return doc, 'Successfully parsed FoLiA XML file.'


def add_entity(sentence, cls, words, text_content_tag, annotation=None):
    entity_tag = '{http://ilk.uvt.nl/folia}entities'
    if sentence.find(entity_tag) is not None:
        entities = sentence.find(entity_tag)
    else:
        entities = etree.SubElement(sentence, 'entities')

    entity = etree.SubElement(entities, 'entity', {'class': cls})
    if not annotation:
        for w in words:
            wref_attrs = {
                'id': w.attrib.get('{http://www.w3.org/XML/1998/namespace}id'),
                't': w.find(text_content_tag).text
            }
            etree.SubElement(entity, 'wref', wref_attrs)
    else:
        for w_id in annotation.word_ids:
            wref_attrs = {
                'id': w_id,
                't': annotation.words.get(w_id)
            }
            etree.SubElement(entity, 'wref', wref_attrs)


def write_folia_file(context, folia_in, dir_out, ext):
    head, tail = os.path.split(folia_in)
    p = tail.split('.')
    file_out = '{d}{s}{n}-{e}.xml'.format(n=p[0], d=dir_out, s=os.sep, e=ext)
    print file_out
    with open(file_out, 'w') as f:
        f.write(etree.tostring(context.root,
                               encoding='utf8',
                               xml_declaration=True,
                               pretty_print=True))
