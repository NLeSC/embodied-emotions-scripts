"""Inspect FoLiA XML file to determine whether it matches our expectations.
Usage: inspect_folia.py <FoLiA XML file>"""

from bs4 import BeautifulSoup, Tag, NavigableString


def tag_or_string(tag):
    """Depending on the type of the input, print the tag name (for Tags) or 
    string (for NavigableStrings). Is used to print parts of the xml file that
    were not expected."""
    if isinstance(tag, Tag):
        return '<{n}>'.format(n=tag.name)
    elif isinstance(tag, NavigableString):
        return tag.string
    else:
        return 'No tag, no string: {t}'.format(t=tag)


def is_tag(tag, name, class_=None):
    if class_:
        return isinstance(tag, Tag) and \
               tag.name == name and tag.get('class') == class_
    else:
        return isinstance(tag, Tag) and tag.name == name


def scene(tag):
    return is_tag(tag, 'div', 'scene')


def act(tag):
    return is_tag(tag, 'div', 'act')


def sub_act(tag):
    return act(tag.parent)


def stage_direction(tag):
    return is_tag(tag, 'event', 'stage')


def speaker_turn(tag):
    return is_tag(tag, 'event', 'speakerturn')


def event_without_class(tag):
    return is_tag(tag, 'event') and not tag.has_attr('class')


def head(tag):
    return is_tag(tag, 'head')


def line_feed(tag):
    return isinstance(tag, NavigableString) and \
           len(tag.string) == 1 and ord(tag.string[0]) == 10


def text_content(tag):
    return is_tag(tag, 't')


def sentence(tag):
    return is_tag(tag, 's')


def paragraph(tag):
    return is_tag(tag, 'p')


def note(tag):
    return is_tag(tag, 'note')


def ref(tag):
    return is_tag(tag, 'ref')


def list(tag):
    return is_tag(tag, 'list')


def item(tag):
    return is_tag(tag, 'item')


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


if __name__ == '__main__':
    #file_name = '/home/jvdzwaan/Documents/Emotion-mining/nederlab-voorbeeld/vos_002mede03_01.xml'
    #file_name = '/home/jvdzwaan/Documents/Emotion-mining/nederlab-voorbeeld/feit007patr01_01.xml'
    file_name = '/home/jvdzwaan/Documents/Emotion-mining/nederlab-voorbeeld/hoof002door01_01.xml'

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
