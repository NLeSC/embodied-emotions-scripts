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
    all_characters = get_characters(speakerturns)
    #for char, num in characters.iteritems():
    #    print char, num
    num_chars = 5
    characters = all_characters.most_common(num_chars)

    speaker = 'UNKNOWN'

    res_posemo = {}
    res_negemo = {}
    count_posemo = {}
    count_negemo = {}

    for (character, freq) in characters:
        res_posemo[character] = np.array([])
        res_negemo[character] = np.array([])

        count_posemo[character] = 0
        count_negemo[character] = 0

    for turn in speakerturns:
        speaker = extract_character_name(turn.get('actor'))
        
        count_posemo = 0
        count_negemo = 0

        for elem in turn.descendants:
            if entity(elem) and elem.get('class').startswith('liwc-'):
                if elem.get('class') == 'liwc-Posemo':
                    count_posemo += 1
                if elem.get('class') == 'liwc-Negemo':
                    count_negemo += 1

        for (character, freq) in characters:
            if speaker == character:
                res_posemo[character] = np.append(res_posemo[character], float(count_posemo))
                res_negemo[character] = np.append(res_negemo[character], float(count_negemo))
            else: 
                res_posemo[character] = np.append(res_posemo[character], 0.0)
                res_negemo[character] = np.append(res_negemo[character], 0.0)

    print 'Turn,{}'.format(','.join([c for c,f in characters]))

    res_posneg = {}
    for (character, freq) in characters:
        res_posneg[character] = r(res_posemo[character], res_negemo[character])
    
    for i in range(len(res_posneg[character])):
        r_values = [str(res_posneg[c][i]) for c, f in characters]
        print '{},{}'.format((i+1), ','.join(r_values))
