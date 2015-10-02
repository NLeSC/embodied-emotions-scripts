"""Insert KAF annotations into a FoLiA files.
To be used in shell script batch_add_tags.sh!
Usage: python kaf2folia.py <kaf tags file> <folia file>
"""

import argparse
import codecs
from lxml import etree
from datetime import datetime
from embem.emotools.folia_helpers import add_entity


class Annotation:
    def __init__(self, level, label, annotation_id, word_id, word):
        self.level = level
        self.label = label
        self.annotation_id = annotation_id
        self.word_ids = [word_id]
        self.words = {word_id: word}

    def entity_id(self, annotation_class):
        return '{}.{}'.format(annotation_class, self.annotation_id)

    def folia_entity_class(self):
        tag_levels = {
            1: 'Level1',
            2: 'Level2',
            3: 'EmotionLabel',
            4: 'EmotionLabel',
            5: 'HumorModifier',
            6: 'Intensifier'
        }

        return '{}:{}'.format(tag_levels[self.level], self.label)


def add_entity2(entity_layer, annotation, annotation_class):
    return 'Adding {} ({}; {})'.format(annotation.entity_id(annotation_class),
                                       annotation.folia_entity_class(),
                                       ' - '.join(annotation.word_ids))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('tag', help='the name of the KAF tag file '
                        'containing the annotations')
    parser.add_argument('folia', help='the name of the FoLiA XML file ')

    args = parser.parse_args()

    tag_file = args.tag
    folia_file = args.folia

    annotator_name = 'EmbodiedEmotions'
    annotator_set = '{}-set'.format(annotator_name)

    # Load KAF tags file
    with codecs.open(tag_file, 'r', 'utf-8', errors='ignore') as f:
        lines = f.readlines()

    # Tag file is tab separated file
    # Each line contains 24 fields:
    # fields[0]: word id
    # fields[1]: token
    # fields[2]: lemma
    # fields[3]: pos tag
    # fields[4]: empty
    # fields[5]: tag level 1 label
    # fields[6]: tag id (level 1) = annotation id(?)
    # fields[7]: tag level 2 label
    # fields[8]: tag id (level 2)
    # fields[9]: tag level 3 label
    # fields[10]: tag id (level 3)
    # fields[11]: tag level 4 label
    # fields[12]: tag id (level 4)
    # fields[13]: tag level 5 label
    # fields[14]: tag id (level 5)
    # fields[15]: tag level 6 label
    # fields[16]: tag id (level 6)

    # NOT USED IN THE EMBODIED EMOTIONS PROJECT
    # fields[17]: tag level 7 label
    # fields[18]: tag id (level 7)
    # fields[19]: tag level 8
    # fields[20]: tag id (level 8)
    # fields[21]: number (unclear what it means)
    # fields[22]: 'true' (unclear what it means)
    # fields[23]: number (unclear what it means)

    annotations = {}

    # (annotation label, annotation id, level)
    levels = [(5, 6, 1), (7, 8, 2), (9, 10, 3), (11, 12, 4), (13, 14, 5),
              (15, 16, 6)]

    for line in lines:

        fields = line.strip().split('\t')

        for level in levels:
            word_id = fields[0]
            annotation_id = int(fields[level[1]])
            annotation_label = fields[level[0]]

            if annotation_id != 0:

                if not annotations.get(annotation_id):
                    # new annotation
                    annotations[annotation_id] = Annotation(level[2],
                                                            annotation_label,
                                                            annotation_id,
                                                            word_id,
                                                            fields[1])
                else:
                    # known annotation: append word_id
                    annotations[annotation_id].word_ids.append(word_id)
                    annotations[annotation_id].words[word_id] = fields[1]

    order = annotations.keys()
    order.sort()
    print ' Found {} annotations'.format(len(order))

    word_id2annotations = {}
    for a in order:
        ann = annotations[a]
        w_id = ann.word_ids[0]
        if w_id not in word_id2annotations.keys():
            word_id2annotations[w_id] = []
        word_id2annotations[w_id].append(ann)
        #print add_entity2(None, annotations[a], 'embodied_emotions')

    # Load document
    context = etree.iterparse(folia_file,
                              events=('end',),
                              remove_blank_text=True)
    annotations_tag = '{http://ilk.uvt.nl/folia}annotations'
    entity_annotations_tag = '{http://ilk.uvt.nl/folia}entity-annotation'
    sentence_tag = '{http://ilk.uvt.nl/folia}s'
    word_tag = '{http://ilk.uvt.nl/folia}w'
    text_content_tag = '{http://ilk.uvt.nl/folia}t'
    id_tag = '{http://www.w3.org/XML/1998/namespace}id'

    num_annotations_added = 0

    for event, elem in context:
        if elem.tag == annotations_tag:
            add_annotation_tag = True
            entity_annotations = elem.findall(entity_annotations_tag)
            for element in entity_annotations:
                if element.attrib.get('annotator') == annotator_name:
                    add_annotation_tag = False

            # add entity-annotation for embodied emotions
            if add_annotation_tag:
                annotation_attrs = {
                    'annotator': annotator_name,
                    'annotatortype': 'manual',
                    'datetime': datetime.now().isoformat(),
                    'set': annotator_set
                }
                etree.SubElement(elem, 'entity-annotation', annotation_attrs)

        if elem.tag == sentence_tag:
            words = elem.findall(word_tag)
            for word in words:
                w_id = word.attrib.get(id_tag)
                if w_id in word_id2annotations.keys():
                    #print w_id
                    for annotation in word_id2annotations[w_id]:
                        cat_label = 'EmbodiedEmotions-{}'. \
                            format(annotation.folia_entity_class())
                        add_entity(elem, cat_label, None, None, annotation)
                        num_annotations_added += 1

    print ' Added {} entities'.format(num_annotations_added)

    with open(folia_file, 'w') as f:
        f.write(etree.tostring(context.root,
                               encoding='utf8',
                               xml_declaration=True,
                               pretty_print=True))
