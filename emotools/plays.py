"""Functions to generate data about entities that can be used for
visualizations.
"""

from collections import Counter
import numpy as np
import re
from bs4_helpers import entity

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
    res = np.append(zeros, a)
    return np.append(res, zeros)


def r(a1, a2):
    """Calculate Jisk's r measure (not sure it makes sense."""
    res = []
    for i in range(len(a1)):
        if not (a1[i] == 0.0 and a2[i] == 0):
            res.append((a1[i]-a2[i])/(a1[i]+a2[i]))
        else:
            res.append(0.0)

    return np.array(res)


def generate_tick_marks(speakerturns):
    """Generate tick marks for a list of speaker turns. Returns a tuple of two
    lists of tick marks; one for acts and one for scenes.
    """
    # TODO: also return labels for the tick marks
    act_marks = []
    scene_marks = []

    current_act_id = ''
    current_scene_id = ''

    for turn in speakerturns:
        scene_id = turn.parent.get('xml:id')

        # The first scene of an act might not be marked as such in FoLiA (the
        # parent of a speaker turn might be either an act or a scene).
        if turn.parent.get('class') == 'scene':
            act_id = turn.parent.parent.get('xml:id')
        else:
            act_id = scene_id

        if not act_id == current_act_id:
            act_marks.append((speakerturns.index(turn)+1))
            current_act_id = act_id

        if not scene_id == current_scene_id:
            scene_marks.append((speakerturns.index(turn)+1))
            current_scene_id = scene_id

    return act_marks, scene_marks


def get_play_id(soup):
    """Return the play ID."""
    id_str = soup.find('text').get('xml:id')
    return re.sub(r'_\d\d_text', '', id_str)


def xml_id2play_id(xml_id):
    """Return the play id given an xml id from the FoLiA file.
    """
    return xml_id[0:13]


def get_entities(soup, entity_class):
    """Return the list of entities in entity class that occur in the FoLiA XML
    document in soup.
    """
    result = {}

    entities_xml = soup.find_all(entity)
    for e in entities_xml:
        if e.get('class').startswith('{}-'.format(entity_class)):
            result[e.get('class')] = None

    return result.keys()
