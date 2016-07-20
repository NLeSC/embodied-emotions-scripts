from nose.tools import assert_equal, assert_true

from lxml import etree
from codecs import open

from embem.kafnaftag.naf2json import create_mention, get_label, create_event, \
    event_name, process_emotions, add_source_text, add_events, merge_events, \
    add_climax_score
from embem.emotools.heem_utils import heem_labels_en, heem_emotion_labels


assert_equal.__self__.maxDiff = None


def setup():
    global soup
    global soup2
    global emotion
    global text_id
    global source
    global emotion_labels
    global num_sentences
    global tokenid2token
    global termid2tokenid
    global termid2emotionid
    global emotions
    global emoids
    global indexed_emotion

    with open('embem/tests/example_naf.xml', 'rb', encoding='utf-8') as f:
        soup = etree.parse(f)

    tokenid2token = {}
    tokens = soup.findall('.//wf')
    words = []
    num_sentences = int(tokens[-1].get('sent'))

    for token in tokens:
        tokenid = token.get('id')
        tokenid2token[tokenid] = {
            'text': token.text,
            'offset': int(token.get('offset')),
            'length': int(token.get('length'))
        }
        words.append(token.text)
        #print tokenid2token[tokenid]
    text = ' '.join(words)

    termid2tokenid = {}
    terms = soup.findall('.//term')
    for term in terms:
        termid = term.get('id')
        tokenid = term[0][0].get('id')
        termid2tokenid[termid] = tokenid
        #print termid, tokenid

    termid2emotionid = {}
    emotions = {}
    emoids = []
    xml_emotions = soup.findall('.//emotion')
    for e in xml_emotions:
        emotionid = e.get('id')
        xml_emotion = etree.fromstring(etree.tostring(e))
        terms = xml_emotion.findall('.//target')
        labels = xml_emotion.findall('.//externalRef')
        for t in terms:
            termid = t.get('id')
            if termid not in termid2emotionid.keys():
                termid2emotionid[termid] = []
            termid2emotionid[termid].append(emotionid)

        ls = [{'reference': l.get('reference'),
               'resource': l.get('resource'),
               'confidence': float(l.get('confidence', 1.0))} for l in labels]
        emotions[emotionid] = {
            'terms': [t.get('id') for t in terms],
            'heem labels': ls
        }
        # to make sure the order of emotions is the same as before
        # (so the resulting json is exactly the same)
        emoids.append(emotionid)

    #with open('embem/tests/example_naf_confidence.xml', 'rb', encoding='utf-8') as f:
    #    soup2 = etree.parse(f)

    emotion = etree.fromstring('<emotion id="emo1">'
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
                            '</emotion>')
    indexed_emotion = {'heem labels': [{'confidence': 1.0, 'resource': 'heem', 'reference': 'conceptType:bodilyProcess'},
                         {'confidence': 1.0, 'resource': 'heem', 'reference': 'emotionType:anger'},
                         {'confidence': 1.0, 'resource': 'heem:bodyParts', 'reference': 'liver'},
                         {'confidence': 1.0, 'resource': 'heem:clusters', 'reference': 'anger'},
                         {'confidence': 1.0, 'resource': 'heem:posNeg', 'reference': 'negative'}],
         'terms': ['t45', 't46', 't47', 't48', 't49', 't50']}

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

    m = create_mention(indexed_emotion, termid2tokenid, tokenid2token, text_id, source)

    assert_equal(result, m)


def test_get_label():
    l = get_label(tokenid2token, create_mention(indexed_emotion, termid2tokenid, tokenid2token, text_id, source))
    assert_equal('Wat hebje veur met dat Cyteeren', l)


def test_create_event():
    emotion_label = 'conceptType:bodyPart'
    group_score = 100
    year = 1719

    event_object = {
        'actors': {},
        'event': event_name(emotion_label, text_id),
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
    events, num_emotions = process_emotions(text_id, year, source,
                                            emotion_labels,
                                            tokenid2token,
                                            termid2tokenid,
                                            termid2emotionid, emotions,
                                            emoids)

    yield assert_equal, 3, len(events)
    yield assert_equal, 3, num_emotions

    year = 1718
    events, num_emotions = process_emotions(text_id + '2', year, source,
                                            emotion_labels,
                                            tokenid2token,
                                            termid2tokenid,
                                            termid2emotionid, emotions,
                                            emoids)

    yield assert_equal, 3, len(events)
    yield assert_equal, 3, num_emotions


def test_process_emotions_confidence_all():
    # TODO: used soup2
    year = 1719
    events, mention_counter = process_emotions(text_id, year, source,
                                            emotion_labels,
                                            tokenid2token,
                                            termid2tokenid,
                                            termid2emotionid, emotions,
                                            emoids, confidence=0.0)

    yield assert_equal, 2, len(events)
    yield assert_equal, 2, len(mention_counter)


def test_process_emotions_confidence_not_all():
    # TODO: used soup2
    year = 1719
    events, mention_counter = process_emotions(text_id, year, source,
                                            emotion_labels,
                                            tokenid2token,
                                            termid2tokenid,
                                            termid2emotionid, emotions,
                                            emoids, confidence=0.8)

    yield assert_equal, 1, len(events)
    yield assert_equal, 1, len(mention_counter)


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
    events, mention_counter = process_emotions(text_id, year, source,
                                            emotion_labels,
                                            tokenid2token,
                                            termid2tokenid,
                                            termid2emotionid, emotions,
                                            emoids)

    add_events(events, num_sentences, json_object)

    yield assert_equal, 3, len(json_object['timeline']['events'])

    # are events merged?
    add_events(events, num_sentences, json_object)

    yield assert_equal, 6, len(json_object['timeline']['events'])


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
    events, mention_counter = process_emotions(text_id, year, source,
                                            emotion_labels,
                                            tokenid2token,
                                            termid2tokenid,
                                            termid2emotionid, emotions,
                                            emoids)
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
