from nose.tools import assert_equal

from bs4 import BeautifulSoup
from codecs import open

from embem.kafnaftag.naf2json import create_mention, get_label, create_event


def setup():
    global soup
    global emotion
    global text_id

    with open('embem/tests/example_naf.xml', 'rb', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'lxml')

    emotion = BeautifulSoup('<emotion id="emo1">'
                            '<emotion_target/>'
                            '<emotion_holder/>'
                            '<emotion_expression/>'
                            '<span>'
                            '<!-- Wat hebje veur met dat Cyteeren -->'
                            '<target id="t45"/>'
                            '<target id="t46"/>'
                            '<target id="t47"/>'
                            '<target id="t48"/>'
                            '<target id="t49"/>'
                            '<target id="t50"/>'
                            '</span>'
                            '<externalReferences>'
                            '<externalRef reference="conceptType:bodilyProcess" resource="heem"/>'
                            '<externalRef reference="emotionType:anger" resource="heem"/>'
                            '<externalRef reference="liver" resource="heem:bodyParts"/>'
                            '<externalRef reference="anger" resource="heem:clusters"/>'
                            '<externalRef reference="negative" resource="heem:posNeg"/>'
                            '</externalReferences>'
                            '</emotion>', 'lxml')
    text_id = 'text_id'


def test_create_mention():
    result = {'char': ['233', '264'],
              'tokens': ['alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.1',
                         'alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.2',
                         'alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.3',
                         'alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.4',
                         'alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.5',
                         'alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.6'],
              'uri': ['text_id']}

    m = create_mention(emotion, soup, text_id)

    assert_equal(result, m)


def test_get_label():
    l = get_label(soup, create_mention(emotion, soup, text_id))
    assert_equal('Wat hebje veur met dat Cyteeren', l)


def test_create_event():
    emotion_label = 'conceptType:bodyPart'
    group_score = 100
    year = 1719

    event_object = {
        'actors': {},
        'event': emotion_label,
        'group': "{}:{}".format(group_score, text_id),
        'groupName': text_id,
        'groupScore': str(group_score),
        'labels': [],
        'mentions': [],
        'prefLabel': [],
        'time': "17190101"
    }

    assert_equal(event_object, create_event(emotion_label, text_id, year))


#def test_process_emotions():
#    process_emotions(emotions, soup, text_id, year)
