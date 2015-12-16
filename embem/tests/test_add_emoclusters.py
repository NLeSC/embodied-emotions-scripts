from nose.tools import assert_equal

from lxml.etree import tostring, fromstring

from embem.kafnaftag.add_emoclusters import add_cluster_labels


def test_add_cluster_labels_with_confidence():
    emotion_xml = '<emotion id="emo129">' \
                  '<emotion_target/>' \
                  '<emotion_holder/>' \
                  '<emotion_expression/>' \
                  '<span>' \
                  '<!-- moogje voor bekommerd weezen . -->' \
                  '<target id="t7165"/>' \
                  '<target id="t7166"/>' \
                  '<target id="t7167"/>' \
                  '<target id="t7168"/>' \
                  '<target id="t7169"/>' \
                  '</span>' \
                  '<externalReferences>' \
                  '<externalRef confidence="0.222222222222" reference="emotionType:fear" resource="heem"/>' \
                  '<externalRef confidence="0.333333333333" reference="emotionType:worry" resource="heem"/>' \
                  '</externalReferences>' \
                  '</emotion>'
    emotion = fromstring(emotion_xml)
    en2nl = {'fear': 'Angst', 'worry': 'Bezorgdheid'}
    replacements = {"Fear": ["Angst", "Bezorgdheid", "Achterdocht", "Ontzag"]}
    name = 'clusters'

    add_cluster_labels(emotion, en2nl, replacements, name)

    expected = '<emotion id="emo129">' \
               '<emotion_target/>' \
               '<emotion_holder/>' \
               '<emotion_expression/>' \
               '<span>' \
               '<!-- moogje voor bekommerd weezen . -->' \
               '<target id="t7165"/>' \
               '<target id="t7166"/>' \
               '<target id="t7167"/>' \
               '<target id="t7168"/>' \
               '<target id="t7169"/>' \
               '</span>' \
               '<externalReferences>' \
               '<externalRef confidence="0.222222222222" reference="emotionType:fear" resource="heem"/>' \
               '<externalRef confidence="0.333333333333" reference="emotionType:worry" resource="heem"/>' \
               '<externalRef confidence="0.333333333333" reference="fear" resource="heem:clusters"/>' \
               '</externalReferences>' \
               '</emotion>'

    assert_equal(expected, tostring(emotion))


def test_add_cluster_labels_without_confidence():
    emotion_xml = '<emotion id="emo129">' \
                  '<emotion_target/>' \
                  '<emotion_holder/>' \
                  '<emotion_expression/>' \
                  '<span>' \
                  '<!-- moogje voor bekommerd weezen . -->' \
                  '<target id="t7165"/>' \
                  '<target id="t7166"/>' \
                  '<target id="t7167"/>' \
                  '<target id="t7168"/>' \
                  '<target id="t7169"/>' \
                  '</span>' \
                  '<externalReferences>' \
                  '<externalRef reference="emotionType:fear" resource="heem"/>' \
                  '<externalRef reference="emotionType:worry" resource="heem"/>' \
                  '</externalReferences>' \
                  '</emotion>'
    emotion = fromstring(emotion_xml)
    en2nl = {'fear': 'Angst', 'worry': 'Bezorgdheid'}
    replacements = {"Fear": ["Angst", "Bezorgdheid", "Achterdocht", "Ontzag"]}
    name = 'clusters'

    add_cluster_labels(emotion, en2nl, replacements, name)

    expected = '<emotion id="emo129">' \
               '<emotion_target/>' \
               '<emotion_holder/>' \
               '<emotion_expression/>' \
               '<span>' \
               '<!-- moogje voor bekommerd weezen . -->' \
               '<target id="t7165"/>' \
               '<target id="t7166"/>' \
               '<target id="t7167"/>' \
               '<target id="t7168"/>' \
               '<target id="t7169"/>' \
               '</span>' \
               '<externalReferences>' \
               '<externalRef reference="emotionType:fear" resource="heem"/>' \
               '<externalRef reference="emotionType:worry" resource="heem"/>' \
               '<externalRef reference="fear" resource="heem:clusters"/>' \
               '</externalReferences>' \
               '</emotion>'

    assert_equal(expected, tostring(emotion))
