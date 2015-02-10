"""Create data set for visualization assignment
The data set consists of:
<sentence id>\t<emotion label>\t<other label>\t<tagged words>

Usage: python folia2visualization-pairs.py <file in> <output dir>
Or: ./batch_do_python.sh folia2visualization-pairs.py <dir in> <output dir>
(for a directory containing folia files)
"""
from lxml import etree
from bs4 import BeautifulSoup
from emotools.bs4_helpers import sentence, note
import argparse
import codecs
import os
from itertools import product
from collections import Counter
import json


def get_time_period(year):
    year = int(year)
    if year >= 1600 and year < 1660:
        return 'renaissance'
    elif year >= 1660 and year < 1750:
        return 'classisism'
    elif year >= 1750 and year <= 1800:
        return 'enlightenment'
    else:
        return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='the name of the FoLiA XML file that '
                        'should be processed.')
    args = parser.parse_args()

    file_name = args.file

    text_id = file_name[-20:-7]

    result = {}

    # read text metadata
    with codecs.open(file_name, 'rb', 'utf8') as f:
        for line in f.readlines():
            parts = line.split('\t')
            period = get_time_period(parts[1])
            genre = parts[2]

            if period not in result.keys():
                result[period] = Counter()
            result[period][genre] += 1

    for p, data in result.iteritems():
        print p
        for g, f in data.iteritems():
            print '\t', g, f
