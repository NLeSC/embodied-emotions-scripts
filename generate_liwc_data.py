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
from emotools import plays
from emotools.bs4_helpers import speaker_turn, entity

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file_in', help='the name of the FoLiA XML file add '
                        'LIWC entities to')
    args = parser.parse_args()

    file_name = args.file_in
    
    with open(file_name, 'r') as f:
        soup = BeautifulSoup(f, 'xml')

    speakerturns = soup.find_all(speaker_turn)
    all_characters = plays.get_characters(speakerturns)
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
        speaker = plays.extract_character_name(turn.get('actor'))
        
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
        res_posneg[character] = plays.moving_average(plays.r(res_posemo[character], res_negemo[character]))
    
    for i in range(len(res_posneg[character])):
        r_values = [str(res_posneg[c][i]) for c, f in characters]
        print '{},{}'.format((i+1), ','.join(r_values))
