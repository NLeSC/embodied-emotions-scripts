"""Inspect FoLiA XML file to determine whether it matches our expectations.
Usage: inspect_folia.py <FoLiA XML file>"""

from bs4 import BeautifulSoup
from bs4_helpers import tag_or_string, scene, act, sub_act, stage_direction, \
    speaker_turn, event_without_class, head, line_feed, text_content, \
    sentence, paragraph, note, ref, list_, item, event
import argparse
import os


def inspect(elements, expected, not_expected, ignored):
    """Loop over elements, for each element inspect its (direct) children. If 
    a child (can be a tag or a string contained in tags) is in expected,
    nothing happens. The same if the tag is in ignored. If it is another kind
    of tag, a message is printed. Not_expected contains tags that are not
    supposed to appear.
    """
    for elem in elements:
        for child in elem.children:
            ok = False
            for condition in expected:
                if condition(child):
                    ok = True
            for condition in ignored:
                if condition(child):
                    ok = True
            if not ok:
                for msg, condition in not_expected.iteritems():
                    if condition(child):
                        print '{m}: {e}'.format(m=msg, e=child.get('xml:id'))
                        ok = True
                if not ok:
                    print 'Other ({s}): {id_}'.format(s=tag_or_string(child),
                                                      id_=child.get('xml:id'))


def match_t_and_s(elements):
    """Check whether every element in elements has matching <t> and <s> tags.
    """
    for elem in elements:
        t_found = False
        s_found = False
        for child in elem.children:
            if text_content(child):
                t_found = True
            if sentence(child):
                s_found = True
        if not t_found and s_found:
            print '<t> and <s> mismatch: {id_}'.format(id_=elem.get('xml:id'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='the name of the FoLiA XML file to ' \
                        'generate KAF files for')
    args = parser.parse_args()

    file_name = args.file

    with open(file_name) as f:
        soup = BeautifulSoup(f, 'xml')

    # inspect acts
    # expected: heads, scenes, paragraphs, line feeds
    # not expected: sub-acts, other tags and strings
    acts = soup.find_all(act)
    print '# acts:', len(acts)
    
    expected = [head, scene, paragraph, line_feed]
    not_expected = {
        'Sub-act': act
    }
    ignored = [note, ref]
    inspect(acts, expected, not_expected, ignored)

    # inspect scenes
    # expected: heads, stage directions, speaker turns, paragraphs, line feeds
    # not expected: sub-scenes, events withot class attribute, other tags and
    # strings
    # hoof002door01_01 also contains <list> and <item> tags. 
    scenes = soup.find_all(scene)
    print '# scenes:', len(scenes)
    
    expected = [head, stage_direction, speaker_turn, paragraph, line_feed]
    not_expected = {
        'Sub-scene': scene,
        'Event without class': event_without_class
    }
    ignored = [note, ref]
    inspect(scenes, expected, not_expected, ignored)

    # inspect heads
    # expected: text content, sentences, line feeds
    # not expected: other tags and strings
    heads = soup.find_all('head')
    print '# heads:', len(heads)

    expected = [text_content, sentence, line_feed]
    not_expected = {}
    ignored = [note, ref]
    inspect(heads, expected, not_expected, ignored)

    # inspect stage directions
    # expected: text content, sentences, line feeds
    # not expected: other tags and strings
    stage_directions = soup.find_all(stage_direction)
    print '# stage directions:', len(stage_directions)

    expected = [text_content, sentence, line_feed]
    not_expected = {}
    ignored = [note, ref]
    inspect(stage_directions, expected, not_expected, ignored)

    # inspect speaker turns
    # expected: text content, sentences, stage directions, paragraphs, 
    # line feeds
    # not expected: other tags and strings
    speaker_turns = soup.find_all(speaker_turn)
    print '# speaker turns:', len(speaker_turns)

    expected = [text_content, sentence, stage_direction, paragraph, line_feed]
    not_expected = {}
    ignored = [note, ref]
    inspect(speaker_turns, expected, not_expected, ignored)

    # inspect events without class 
    # expected: text content, sentences, line feeds
    # not expected: other tags and strings
    events_without_class = soup.find_all(event_without_class)
    print '# events without class:', len(events_without_class)

    expected = [text_content, sentence, line_feed]
    not_expected = {}
    ignored = [note, ref]
    inspect(events_without_class, expected, not_expected, ignored)

    print 'Match <t> and <s> in <event>s.'
    events = soup.find_all(event)
    match_t_and_s(events)

    print 'Printing all <pos>-tags.'
    pos_coll = {}
    pos_tags = soup.find_all('pos')
    for elem in pos_tags:
        pos_coll[elem.get('head')] = None

    print '\n'.join(pos_coll.keys())
