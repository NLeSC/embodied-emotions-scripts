"""Script that generates data about LIWC entities that can be used for
visualizations.
"""

from bs4 import BeautifulSoup
from datetime import datetime
import argparse
import codecs
import os
from collections import Counter

from emotools.bs4_helpers import speaker_turn, sentence, entity

def get_characters(speakerturns):
    """Return a list of characters based a list of speaker turns."""
    characters = Counter()
    for turn in speakerturns:
        # more postprocessing required for character names (character names
        # now sometimes include stage directions)
        actor = turn['actor'].strip()
        characters[actor] += 1
    return characters

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file_in', help='the name of the FoLiA XML file add '
                        'LIWC entities to')
    args = parser.parse_args()

    file_name = args.file_in
    
    with open(file_name, 'r') as f:
        soup = BeautifulSoup(f, 'xml')

    speakerturns = soup.find_all(speaker_turn)
    characters = get_characters(speakerturns)
    #for char, num in characters.iteritems():
    #    print char, num

    character = 'Eloiza.'

    print 'Sentence,{},{},{}'.format('affect', 'posemo', 'negemo')

    sent = 0
    speaker = 'UNKNOWN'
    count_affect = 0
    count_posemo = 0
    count_negemo = 0
    for elem in soup.descendants:
        if speaker_turn(elem):
            speaker = elem.get('actor').strip()
        elif sentence(elem):
            if count_affect > 0 or count_posemo > 0 or count_negemo > 0:
                if speaker == character:
                    print '{},{},{},{}'.format(sent,
                                               count_affect,
                                               count_posemo,
                                               count_negemo)
                count_affect = 0
                count_posemo = 0
                count_negemo = 0
            sent += 1
        elif entity(elem) and elem.get('class').startswith('liwc-'):
            if elem.get('class') == 'liwc-Affect':
                count_affect += 1
            if elem.get('class') == 'liwc-Posemo':
                count_posemo += 1
            if elem.get('class') == 'liwc-Negemo':
                count_negemo += 1
