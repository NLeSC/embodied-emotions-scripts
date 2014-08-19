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
import sys
import re

from emotools.bs4_helpers import speaker_turn, sentence, entity

def get_characters(speakerturns):
    """Return a list of characters based a list of speaker turns."""
    characters = Counter()
    for turn in speakerturns:
        # more postprocessing required for character names (character names
        # now sometimes include stage directions)
        actor_string = turn['actor']
        actor = extract_character_name(actor_string)
        characters[actor] += 1
    return characters


def extract_character_name(actor_str):
    """Returns the character name extracted from the input string."""
    actor_str = actor_str.replace('(', '').replace(')', '')
    actor_str = actor_str.replace('[', '').replace(']', '')
    actor_str = actor_str.replace('van binnen', '')
    parts = re.split('[.,]', actor_str)
    return parts[0].strip()


def moving_average(a, n=3):
    """Calculate the moving average of array a and window size n."""
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def add_leading_and_trailing_zeros(a, n):
    """Return array a with n/2 leading and trailing zeros."""
    zeros = [0] * (n/2)
    res =  np.append(zeros, a)
    return np.append(res, zeros)


def r(a1, a2):
    """Calculate Jisk's r measure (not sure it makes sense."""
    res = []
    for i in range(len(a1)):
        if not a1[i] == 0.0 or not a2[i] == 0:
            res.append((a1[i]-a2[i])/(a1[i]+a2[i]))
        else:
            res.append(0.0)

    return np.array(res)


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

    character = 'Eloiza'

    sent = 0
    speaker = 'UNKNOWN'
    count_affect = 0
    count_posemo = 0
    count_negemo = 0
    res_affect = np.array([])
    res_posemo = np.array([])
    res_negemo = np.array([])

    for turn in speakerturns:
        count_affect = 0
        count_posemo = 0
        count_negemo = 0

        speaker = extract_character_name(turn.get('actor'))

        for elem in turn.descendants:
            if entity(elem) and elem.get('class').startswith('liwc-'):
                if elem.get('class') == 'liwc-Affect':
                    count_affect += 1
                if elem.get('class') == 'liwc-Posemo':
                    count_posemo += 1
                if elem.get('class') == 'liwc-Negemo':
                    count_negemo += 1

        if speaker == character:
            res_affect = np.append(res_affect, float(count_affect))
            res_posemo = np.append(res_posemo, float(count_posemo))
            res_negemo = np.append(res_negemo, float(count_negemo))
        else: 
            res_affect = np.append(res_affect, 0.0)
            res_posemo = np.append(res_posemo, 0.0)
            res_negemo = np.append(res_negemo, 0.0)

    print 'Turn,{}'.format(character)

    res_posneg = r(res_posemo, res_negemo)
    s = 1

    for i in range(len(res_posemo)):
        v1 = res_posemo[i]
        v2 = res_negemo[i]
        v3 = res_posneg[i]

        #print '{},{},{},{}'.format(s, v1, -v2, v3)
        print '{},{}'.format(s, v3)
        s += 1
