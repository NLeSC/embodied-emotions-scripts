"""Script to save data from the entity_vis/embem_entity_graph_title graph to
csv.

This script was used to generate a csv file of the embodied emotions posemo/
negemo graph of Achilles (in Article 2), because the reviewers wanted us to
add labels and a legend, etc.

To get a json object start the visualization app and go to
http://127.0.0.1:8000/entity_vis/embem_entity_graph_title/<title id>/
and choose 'save as'

usage: python embem/visualizationdata/json2csv.py <json file> <out file>
"""

import argparse
import json

import pandas as pd

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('json', help='json object containing data of posemo/'
                        'negemo graph')
    parser.add_argument('outfile', help='nams of the csv file where the data '
                        'should be saved')
    args = parser.parse_args()

    json_in = args.json
    out_file = args.outfile

    with open(json_in) as f:
        data = json.load(f)

    result = {}

    for s in data['graph']:
        result[s['key']] = [d['Score'] for d in s['values']]
        l = len(s['values'])

    r = pd.DataFrame(result, index=range(1, l+1))
    r.to_csv(out_file, encoding='utf-8')
