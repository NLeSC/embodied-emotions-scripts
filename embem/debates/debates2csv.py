#!/usr/bin/env python
# -.*- coding: utf-8 -.*-
"""Script to extract counts for words in word field.

Usage: debates2csv.py <xml-file or directory containing xml files>

2014-11-18 j.vanderzwaan@esciencecenter.nl
"""
import argparse
import xml.etree.ElementTree as ET
import re
from collections import Counter
import os


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('xml', help='the name of the xml file containing the '
                        'the word field counts should be extracted for')
    args = parser.parse_args()

    # file or directory?
    if os.path.isfile(args.xml):
        files = [args.xml]
    else:
        files = []
        for fn in os.listdir(args.xml):
            file_name = '{}{}{}'.format(args.xml, os.sep, fn)
            if os.path.isfile(file_name):
                files.append(file_name)

    # a list of the LIWC anger words
    # abuse.* means that any word starting with 'abuse' (e.g., 'abuser' or
    # 'abuses') is counted.
    word_field = ['abuse.*', 'abusi.*', 'aggravat.*', 'aggress.*', 'agitat.*',
                  'anger.*', 'angr.*', 'annoy.*', 'antagoni.*', 'argh.*',
                  'argu.*', 'arrogan.*', 'assault.*', 'asshole.*', 'attack.*',
                  'bastard.*', 'battl.*', 'beaten', 'bitch.*', 'bitter.*',
                  'blam.*', 'bother.*', 'brutal.*', 'cheat.*', 'confront.*',
                  'contempt.*', 'contradic.*', 'crap', 'crappy', 'critical',
                  'critici.*', 'crude.*', 'cruel.*', 'cunt.*', 'cut', 'cynic',
                  'damn.*', 'danger.*', 'defenc.*', 'defens.*', 'despis.*',
                  'destroy.*', 'destruct.*', 'disgust.*', 'distrust.*',
                  'domina.*', 'dumb.*', 'dump.*', 'enemie.*', 'enemy.*',
                  'enrag.*', 'envie.*', 'envious', 'envy.*', 'evil.*',
                  'feroc.*', 'feud.*', 'fiery', 'fight.*', 'foe.*', 'fought',
                  'frustrat.*', 'fuck', 'fucked.*', 'fucker.*', 'fuckin.*',
                  'fucks', 'fume.*', 'fuming', 'furious.*', 'fury', 'goddam.*',
                  'greed.*', 'grouch.*', 'grr.*', 'harass.*', 'hate', 'hated',
                  'hateful.*', 'hater.*', 'hates', 'hating', 'hatred',
                  'heartless.*', 'hell', 'hellish', 'hit', 'hostil.*',
                  'humiliat.*', 'idiot.*', 'insult.*', 'interrup.*',
                  'intimidat.*', 'jealous.*', 'jerk', 'jerked', 'jerks',
                  'kill.*', 'liar.*', 'lied', 'lies', 'lous.*', 'ludicrous.*',
                  'lying', 'mad', 'maddening', 'madder', 'maddest', 'maniac.*',
                  'mock', 'mocked', 'mocker.*', 'mocking', 'mocks', 'molest.*',
                  'moron.*', 'murder.*', 'nag.*', 'nast.*', 'obnoxious.*',
                  'offence.*', 'offend.*', 'offens.*', 'outrag.*', 'paranoi.*',
                  'pettie.*', 'petty.*', 'piss.*', 'poison.*', 'prejudic.*',
                  'prick.*', 'protest', 'protested', 'protesting', 'punish.*',
                  'rage.*', 'raging', 'rape.*', 'raping', 'rapist.*',
                  'rebel.*', 'resent.*', 'revenge.*', 'ridicul.*', 'rude.*',
                  'sarcas.*', 'savage.*', 'sceptic.*', 'screw.*', 'shit.*',
                  'sinister', 'skeptic.*', 'smother.*', 'snob.*', 'spite.*',
                  'stubborn.*', 'stupid.*', 'suck', 'sucked', 'sucker.*',
                  'sucks', 'sucky', 'tantrum.*', 'teas.*', 'temper', 'tempers',
                  'terrify', 'threat.*', 'ticked', 'tortur.*', 'trick.*',
                  'ugl.*', 'vicious.*', 'victim.*', 'vile', 'villain.*',
                  'violat.*', 'violent.*', 'war', 'warfare.*', 'warred',
                  'warring', 'wars', 'weapon.*', 'wicked.*']

    num_words = 0
    all_words = Counter()
    wf_words = Counter()

    for input_file in files:
        # read xml file
        tree = ET.parse(input_file)
        root = tree.getroot()

        for speech in tree.getiterator('speech'):
            speaker = speech.attrib.get('speaker')
            text = ET.tostring(speech)

            # remove xml tags
            text = re.sub('<[^>]*>', '', text)
            # remove html entities (e.g., &#611;)
            text = re.sub('&#\d+;', '', text)
            # convert to lower case
            text = text.lower()

            # extract a list of words
            words = re.findall('\w+', text)

            # count words
            num_words += len(words)
            all_words.update(words)

    regex = re.compile('^{}$'.format('$|^'.join(word_field)))

    # count word field words
    for word in all_words:
        if regex.match(word):
            wf_words[word] += all_words[word]

    # print output
    print 'Word\tFrequency'
    print 'TOTAL\t{}'.format(num_words)
    for (word, freq) in wf_words.most_common():
        print '{}\t{}'.format(word, freq)
