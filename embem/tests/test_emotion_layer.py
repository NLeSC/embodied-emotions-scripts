from nose.tools import assert_equal, assert_true, assert_false

from bs4 import BeautifulSoup
from lxml.etree import Element, tostring, fromstring

from embem.kafnaftag.emotions_layer import lowerc, embem_entity, add_targets, \
    naf_emotion, get_second_part,add_external_reference


def test_lowerc():
    strs = {'BodyPart': 'bodyPart',
            'bodyPart': 'bodyPart',
            'BODYPART': 'bODYPART'}
    for k, v in strs.iteritems():
        yield assert_equal, lowerc(k), v


def test_embem_entity_true():
    xml_doc = """
    <entities xml:id="alew001besl01_01.TEI.2.text.body.div.div.sp.614.s.1.entities.1">
        <entity class="EmbodiedEmotions-Level1:Lichaamswerking">
            <wref id="alew001besl01_01.TEI.2.text.body.div.div.sp.614.s.1.w.5" t="maek"/>
            <wref id="alew001besl01_01.TEI.2.text.body.div.div.sp.614.s.1.w.6" t="my"/>
            <wref id="alew001besl01_01.TEI.2.text.body.div.div.sp.614.s.1.w.7" t="de"/>
            <wref id="alew001besl01_01.TEI.2.text.body.div.div.sp.614.s.1.w.8" t="kop"/>
            <wref id="alew001besl01_01.TEI.2.text.body.div.div.sp.614.s.1.w.9" t="niet"/>
            <wref id="alew001besl01_01.TEI.2.text.body.div.div.sp.614.s.1.w.10" t="warm"/>
        </entity>
    </entities>"""

    soup = BeautifulSoup(xml_doc, 'xml')
    elem = soup.find('entity')

    assert_true(embem_entity(elem))


def test_embem_entity_false():
    xml_doc = """
    <entities xml:id="alew001besl01_01.TEI.2.text.body.div.div.sp.614.s.1.entities.1">
        <entity xml:id="alew001besl01_01.TEI.2.text.body.div.div.sp.614.s.1.entities.1.entity.1" class="per" confidence="0.312152">
            <wref id="alew001besl01_01.TEI.2.text.body.div.div.sp.614.s.1.w.3" t="Swaen"/>
        </entity>
    </entities>"""

    soup = BeautifulSoup(xml_doc, 'xml')
    elem = soup.find('entity')

    assert_false(embem_entity(elem))


def test_add_targets():
    emotion = Element('emotion', id='emo125')
    words = ['huilende', ',', 'hikkende', 'en', 'snikkende']
    ids = ['t2875', 't2876', 't2877', 't2878', 't2879']

    add_targets(emotion, words, ids)
    result = tostring(emotion)

    expected = '<emotion id="emo125"><span><!-- huilende , hikkende en ' \
               'snikkende --><target id="t2875"/><target id="t2876"/>' \
               '<target id="t2877"/><target id="t2878"/><target id="t2879"/>' \
               '</span></emotion>'

    assert_equal(result, expected)


def test_naf_emotion():
    data = {'labels': ['Lichaamswerking', 'Verdriet'],
            'tids': ['t2875', 't2876', 't2877', 't2878', 't2879'],
            'words': ['huilende', ',', 'hikkende', 'en', 'snikkende'],
            'confidence': [1.0, 1.0]}
    emo_id = 125
    emotion, emo_id_new = naf_emotion(data, emo_id)

    expected = '<emotion id="emo125">' \
               '<emotion_target/>' \
               '<emotion_holder/>' \
               '<emotion_expression/>' \
               '<span>' \
               '<!-- huilende , hikkende en snikkende -->' \
               '<target id="t2875"/>' \
               '<target id="t2876"/>' \
               '<target id="t2877"/>' \
               '<target id="t2878"/>' \
               '<target id="t2879"/>' \
               '</span>' \
               '<externalReferences>' \
               '<externalRef confidence="1.0" reference="conceptType:bodilyProcess" resource="heem"/>' \
               '<externalRef confidence="1.0" reference="emotionType:sadness" resource="heem"/>' \
               '</externalReferences>' \
               '</emotion>'
    yield assert_equal, expected, tostring(emotion)
    yield assert_equal, emo_id + 1, emo_id_new


def test_naf_emotion_humormodifier():
    data = {'labels': ['warm'],
            'tids': ['t2875'],
            'words': ['huilende'],
            'confidence': [1.0]}
    emo_id = 125
    emotion, emo_id_new = naf_emotion(data, emo_id)

    expected = '<emotion id="emo125">' \
               '<emotion_target/>' \
               '<emotion_holder/>' \
               '<emotion_expression/>' \
               '<span>' \
               '<!-- huilende -->' \
               '<target id="t2875"/>' \
               '</span>' \
               '<externalReferences>' \
               '<externalRef confidence="1.0" reference="humorModifier:warm" resource="heem"/>' \
               '</externalReferences>' \
               '</emotion>'
    yield assert_equal, expected, tostring(emotion)
    yield assert_equal, emo_id + 1, emo_id_new


def test_naf_emotion_intensifier():
    data = {'labels': ['versterkend'],
            'tids': ['t2875'],
            'words': ['huilende'],
            'confidence': [1.0]}
    emo_id = 125
    emotion, emo_id_new = naf_emotion(data, emo_id)

    expected = '<emotion id="emo125">' \
               '<emotion_target/>' \
               '<emotion_holder/>' \
               '<emotion_expression/>' \
               '<span>' \
               '<!-- huilende -->' \
               '<target id="t2875"/>' \
               '</span>' \
               '<externalReferences>' \
               '<externalRef confidence="1.0" reference="intensifier:intensifying" resource="heem"/>' \
               '</externalReferences>' \
               '</emotion>'
    yield assert_equal, expected, tostring(emotion)
    yield assert_equal, emo_id + 1, emo_id_new


def test_get_second_part():
    annotations = {"EmbodiedEmotions-Intensifier:versterkend": 'versterkend',
                   "EmbodiedEmotions-EmotionLabel:Blijdschap": 'Blijdschap',
                   "EmbodiedEmotions-HumorModifier:zoet": 'zoet',
                   "EmbodiedEmotions-Level1:Lichaamswerking": 'Lichaamswerking',
                   "EmbodiedEmotions-Level2:Lichaamsdeel": 'Lichaamsdeel',
                   "EmbodiedEmotions-Level1:EmotioneleHandeling": 'EmotioneleHandeling'}
    for k, v in annotations.iteritems():
        yield assert_equal, get_second_part(k), v


def test_naf_emotion_expanded_bodyparts():
    data = {'labels': ['Lichaamsdeel'],
            'tids': ['t2875', 't2876', 't2877', 't2878', 't2879'],
            'words': ['hertelijck', ',', 'hikkende', 'en', 'snikkende'],
            'confidence': [0.25]}
    emo_id = 125
    bpmapping = {u'hertelijck': u'heart'}
    emotion, emo_id_new = naf_emotion(data, emo_id, bpmapping)

    expected = '<emotion id="emo125">' \
               '<emotion_target/>' \
               '<emotion_holder/>' \
               '<emotion_expression/>' \
               '<span>' \
               '<!-- hertelijck , hikkende en snikkende -->' \
               '<target id="t2875"/>' \
               '<target id="t2876"/>' \
               '<target id="t2877"/>' \
               '<target id="t2878"/>' \
               '<target id="t2879"/>' \
               '</span>' \
               '<externalReferences>' \
               '<externalRef confidence="0.25" reference="conceptType:bodyPart" resource="heem"/>' \
               '<externalRef confidence="0.25" reference="heart" resource="heem:bodyParts"/>' \
               '</externalReferences>' \
               '</emotion>'
    yield assert_equal, expected, tostring(emotion)


def test_add_external_reference_no_external_references_layer():
    # in: emotion without externalReferences
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
                  '</emotion>'
    emotion = fromstring(emotion_xml)
    resource = 'heem-manual_annotations'
    reference = 'emotionType:fear'
    confidence = '0.222222222222'
    add_external_reference(emotion, resource, reference, confidence)

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
               '<externalRef confidence="0.222222222222" reference="emotionType:fear" resource="heem-manual_annotations"/>' \
               '</externalReferences>' \
               '</emotion>'

    assert_equal(expected, tostring(emotion))


def test_add_external_reference_with_existing_external_reference_layer():
    # in: emotion with externalReferences
    # in: wel confidence
    # in: no confidence value
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
                  '</externalReferences>' \
                  '</emotion>'
    emotion = fromstring(emotion_xml)
    resource = 'heem-manual_annotations'
    reference = 'emotionType:fear'
    confidence = '0.222222222222'
    add_external_reference(emotion, resource, reference, confidence)

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
               '<externalRef confidence="0.222222222222" reference="emotionType:fear" resource="heem-manual_annotations"/>' \
               '</externalReferences>' \
               '</emotion>'

    assert_equal(expected, tostring(emotion))


def test_add_external_reference_with_existing_external_reference_layer():
    # in: emotion with externalReferences
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
                  '</emotion>'
    emotion = fromstring(emotion_xml)
    resource = 'heem-manual_annotations'
    reference = 'emotionType:fear'
    add_external_reference(emotion, resource, reference, None)

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
               '<externalRef reference="emotionType:fear" resource="heem-manual_annotations"/>' \
               '</externalReferences>' \
               '</emotion>'

    assert_equal(expected, tostring(emotion))
