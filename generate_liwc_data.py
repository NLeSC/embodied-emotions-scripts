"""Script that generates data about LIWC entities that can be used for
visualizations.
"""

from bs4 import BeautifulSoup
from datetime import datetime
import argparse
import codecs
import os
from collections import Counter
import numpy as np

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


def moving_average(a, n=3):
    """Calculate the moving average of array a and window size n."""
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


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

    #print 'Sentence,{},{},{}'.format('affect', 'posemo', 'negemo')
    print 'Sentence,{},{}'.format('affect', 'smooth')

    sent = 0
    speaker = 'UNKNOWN'
    count_affect = 0
    count_posemo = 0
    count_negemo = 0
    res_affect = np.array([])

    for elem in soup.descendants:
        if speaker_turn(elem):
            speaker = elem.get('actor').strip()
        elif sentence(elem):
            if speaker == character:
                res_affect = np.append(res_affect, float(count_affect))
                #print '{},{},{},{}'.format(sent,
                #                           count_affect,
                #                           count_posemo,
                #                           count_negemo)
            else: 
                res_affect = np.append(res_affect, 0.0)
            
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

    #print 'aantal zinnen:', sent, len(soup.find_all(sentence))
    #print 'lengte res_affect array:', len(res_affect)
    #print res_affect

    s = 1
    window = 5 
    res_affect_smooth = moving_average(res_affect, window)
    for i in range(len(res_affect)):
        a = res_affect[i]
        if i > window/2 and i < len(res_affect_smooth):
            a_sm = res_affect_smooth[i-window/2]
        else:
            a_sm = 0.0

        print '{},{},{}'.format(s, a, a_sm)
        s += 1

