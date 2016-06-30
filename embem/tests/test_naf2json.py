from nose.tools import assert_equal, assert_true

from bs4 import BeautifulSoup
from codecs import open

from embem.kafnaftag.naf2json import create_mention, get_label, create_event, \
    event_name, process_emotions, get_num_sentences, get_text, \
    add_source_text, add_events, merge_events, add_climax_score
from embem.emotools.heem_utils import heem_labels_en, heem_emotion_labels


assert_equal.__self__.maxDiff = None


def setup():
    global soup
    global soup2
    global emotion
    global text_id
    global source
    global emotion_labels

    with open('embem/tests/example_naf.xml', 'rb', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'lxml')

    with open('embem/tests/example_naf_confidence.xml', 'rb', encoding='utf-8') as f:
        soup2 = BeautifulSoup(f, 'lxml')

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
    source = 'Wat hebje veur met dat Cyteeren'
    emotion_labels = [heem_labels_en[l].lower() for l in heem_emotion_labels]


def test_create_mention():
    result = {'char': ['233', '264'],
              'perspective': [{'source': '{}'.format(source)}],
              'tokens': ['alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.1',
                         'alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.2',
                         'alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.3',
                         'alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.4',
                         'alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.5',
                         'alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.6'],
              'uri': ['text_id']}

    m = create_mention(emotion, soup, text_id, source)

    assert_equal(result, m)


def test_get_label():
    l = get_label(soup, create_mention(emotion, soup, text_id, source))
    assert_equal('Wat hebje veur met dat Cyteeren', l)


def test_create_event():
    emotion_label = 'conceptType:bodyPart'
    group_score = 100
    year = 1719

    event_object = {
        'actors': {},
        'event': event_name(emotion_label, year),
        'group': emotion_label,
        'groupName': emotion_label,
        'groupScore': str(group_score),
        'labels': [],
        'mentions': [],
        'prefLabel': [],
        'time': "17190101"
    }

    assert_equal(event_object, create_event(emotion_label, text_id, year))


def test_event_name():
    assert_equal('emotionType:joy_text_id', event_name('emotionType:joy', text_id))


def test_process_emotions():
    # check whether the events object and the mention_counter are reset for
    # each text
    year = 1719
    events, mention_counter = process_emotions(soup, text_id, year, source, emotion_labels)

    yield assert_equal, 3, len(events)
    yield assert_equal, 3, len(mention_counter)

    year = 1718
    events, mention_counter = process_emotions(soup, text_id+'2', year, source, emotion_labels)

    yield assert_equal, 3, len(events)
    yield assert_equal, 3, len(mention_counter)


def test_process_emotions_confidence_all():
    year = 1719
    events, mention_counter = process_emotions(soup2, text_id, year, source, emotion_labels, confidence=0.0)

    yield assert_equal, 2, len(events)
    yield assert_equal, 2, len(mention_counter)


def test_process_emotions_confidence_not_all():
    year = 1719
    events, mention_counter = process_emotions(soup2, text_id, year, source, emotion_labels, confidence=0.8)

    yield assert_equal, 1, len(events)
    yield assert_equal, 1, len(mention_counter)


def test_get_num_sentences():
    assert_equal(12, get_num_sentences(soup))


def test_get_text():
    t = "Beslikte Swaantje , en Drooge Fobert ; of de boere rechtbank . Eerste bedryf . Eerste tooneel . Het Tooneel verbeeldeenig Geboomte , in 't verschiet een Heeren Huis . Crelis , en Kryn , malkander en op den weg ontmoetende . Crelis . Wat hebje veur met dat Cyteeren ? Wat meug jy leggen prossedeeren ? Myn goeje man ; 'k lag met jou plyt ; Ho , Kryn , je bent het byltje kwyt . Kryn . Wel , ouwe Cees , hoe keunje praeten ? 'k Zeg noch , ik zel 't ' er niet by laeten , Al zouw het onderst boven staen ; Lag jy vry uit ; 't zal zo niet gaen ."
    assert_equal(t, get_text(soup))


def test_add_source_text():
    json_object = {
        'timeline': {
            'events': [],
            'sources': []
        }
    }
    add_source_text(soup, text_id, json_object)

    r = {
        'timeline': {
            'events': [],
            'sources': [{'uri': text_id, 'text': get_text(soup)}]
        }
    }

    yield assert_equal, r, json_object


def test_add_events():
    # make sure that events are not added multiple time (keep track of counts)
    year = 1918
    json_object = {
        'timeline': {
            'events': [],
            'sources': []
        }
    }
    events, mention_counter = process_emotions(soup, text_id, year, source, emotion_labels)
    num_sentences = get_num_sentences(soup)

    add_events(events, num_sentences, json_object)

    yield assert_equal, 3, len(json_object['timeline']['events'])

    # are events merged?
    add_events(events, num_sentences, json_object)

    yield assert_equal, 3, len(json_object['timeline']['events'])


def test_merge_events():
    event1 = {
                "actors": {
                    "liver": [
                        "liver"
                    ]
                },
                "climax": 1.0,
                "event": "anger_1715",
                "group": "anger",
                "groupName": "anger",
                "groupScore": "100",
                "labels": [
                    "Wat hebje veur met dat Cyteeren"
                ],
                "mentions": [
                    {
                        "char": [
                            "233",
                            "264"
                        ],
                        "perspective": [
                            {
                                "source": "Beslikte Swaantje en drooge Fobert - Abraham Alewijn"
                            }
                        ],
                        "tokens": [
                            "alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.1",
                            "alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.2",
                            "alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.3",
                            "alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.4",
                            "alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.5",
                            "alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.6"
                        ],
                        "uri": [
                            "alew001besl01"
                        ]
                    }
                ],
                "prefLabel": [
                    "anger_1715"
                ],
                "time": "17150101"
            }
    event2 = {
                "actors": {
                    "tears": [
                        "tears"
                    ]
                },
                "climax": 1.0,
                "event": "anger_1715",
                "group": "anger",
                "groupName": "anger",
                "groupScore": "100",
                "labels": [
                    "Zeg"
                ],
                "mentions": [
                    {
                        "char": [
                            "426",
                            "429"
                        ],
                        "perspective": [
                            {
                                "source": "Beslikte Swaantje en drooge Fobert - Abraham Alewijn"
                            }
                        ],
                        "tokens": [
                            "alew001besl01_01.TEI.2.text.body.div.div.sp.237.s.2.w.2"
                        ],
                        "uri": [
                            "alew001besl01"
                        ]
                    }
                ],
                "prefLabel": [
                    "sadness_1715"
                ],
                "time": "17150101"
            }
    merged = {
                "actors": {
                    "liver": [
                        "liver"
                    ],
                    "tears": [
                        "tears"
                    ]
                },
                "climax": 2.0,
                "event": "anger_1715",
                "group": "anger",
                "groupName": "anger",
                "groupScore": "100",
                "labels": [
                    "Wat hebje veur met dat Cyteeren",
                    "Zeg"
                ],
                "mentions": [
                    {
                        "char": [
                            "233",
                            "264"
                        ],
                        "perspective": [
                            {
                                "source": "Beslikte Swaantje en drooge Fobert - Abraham Alewijn"
                            }
                        ],
                        "tokens": [
                            "alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.1",
                            "alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.2",
                            "alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.3",
                            "alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.4",
                            "alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.5",
                            "alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.6"
                        ],
                        "uri": [
                            "alew001besl01"
                        ]
                    },
                    {
                        "char": [
                            "426",
                            "429"
                        ],
                        "perspective": [
                            {
                                "source": "Beslikte Swaantje en drooge Fobert - Abraham Alewijn"
                            }
                        ],
                        "tokens": [
                            "alew001besl01_01.TEI.2.text.body.div.div.sp.237.s.2.w.2"
                        ],
                        "uri": [
                            "alew001besl01"
                        ]
                    }
                ],
                "prefLabel": [
                    "anger_1715"
                ],
                "time": "17150101"
            }

    result = merge_events(event1, event2)

    yield assert_equal, merged, result


def test_add_events_climax_score():
    year = 1918
    json_object = {
        'timeline': {
            'events': [],
            'sources': []
        }
    }
    events, mention_counter = process_emotions(soup, text_id, year, source, emotion_labels)
    num_sentences = get_num_sentences(soup)
    add_events(events, num_sentences, json_object)

    # every event has a climax score
    for e in json_object['timeline']['events']:
        yield assert_true, e.get('climax')
        yield assert_equal, len(e['mentions'])+0.0/num_sentences*100, e.get('climax')


def test_add_climax_score():
    event = {
                "actors": {
                    "liver": [
                        "liver"
                    ]
                },
                "event": "anger_1715",
                "group": "anger",
                "groupName": "anger",
                "groupScore": "100",
                "labels": [
                    "Wat hebje veur met dat Cyteeren"
                ],
                "mentions": [
                    {
                        "char": [
                            "233",
                            "264"
                        ],
                        "perspective": [
                            {
                                "source": "Beslikte Swaantje en drooge Fobert - Abraham Alewijn"
                            }
                        ],
                        "tokens": [
                            "alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.1",
                            "alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.2",
                            "alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.3",
                            "alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.4",
                            "alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.5",
                            "alew001besl01_01.TEI.2.text.body.div.div.sp.225.s.1.w.6"
                        ],
                        "uri": [
                            "alew001besl01"
                        ]
                    }
                ],
                "prefLabel": [
                    "anger_1715"
                ],
                "time": "17150101"
            }
    add_climax_score(event, 1)

    assert_equal(event.get('climax'), 1.0)
