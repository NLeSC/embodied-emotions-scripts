"""Helper functions for using BeautifulSoup to work with FoLiA XML files. 
"""

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


def list_(tag):
    return is_tag(tag, 'list')


def item(tag):
    return is_tag(tag, 'item')


def word(tag):
    return is_tag(tag, 'w')
