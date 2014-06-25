"""Create KAF file based on FoLiA file
Usage: python kaf2folia.py <file in>
"""
from pynlpl.formats import folia
from lxml import etree

# Load document
doc = folia.Document(file='medea-folia-no_events.xml')

# output document
root = etree.Element('KAF')
kaf_document = etree.ElementTree(root)
text = etree.SubElement(root, 'text')

# words
for paragraph in doc.paragraphs():
    for sentence in paragraph.sentences():
        for word in sentence.words():
            w = etree.SubElement(text, 'wf', wid=word.id, sent=sentence.id,
                                 para=paragraph.id)
            w.text = unicode(word)

print etree.tostring(kaf_document, pretty_print=True)
