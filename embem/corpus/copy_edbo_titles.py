"""Script that copies the files of edbo titles that are both available and
selected.

For convenience hard coded file paths are used.

Usage: python copy_edbo_titles.py
"""

import pandas as pd
import glob
import shutil
import os
import re
import requests
from bs4 import BeautifulSoup


def get_file_id(row):
    #print row
    #print type(row['file'])
    if type(row['file']) is str:
        a = row['file'].split('-')[-1]
    else:
        a = None
    #print a
    return a


def get_delpher_id(row):
    if type(row['delpher']) is str:
        a = int(row['delpher'].split(':')[1])
    else:
        a = None
    #print a
    return a


def copy_file(row):
    output_dir = '/home/jvdzwaan/data/edbo/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    fs = glob.glob('/home/jvdzwaan/Downloads/FROG/*{}*.gz'.format(row['file_id']))
    if len(fs) == 1:
        shutil.copy(fs[0], output_dir)
        return os.path.basename(fs[0]).replace('.xml.gz', '')
    elif len(fs) == 0:
        print 'No file found for {}'.format(row['title'])
    else:
        print 'Multiple files found for {}'.format(row['title'])

    return None


def get_genre(row):
    replacements = {'treurspel': 'tragedie/treurspel',
                    'klugt': 'klucht',
                    'klucht': 'klucht'}

    for s, r in replacements.iteritems():
        if re.search(s, row['title'], re.I):
            return r
    return 'unknown'


def get_year(row):
    url_template = 'http://www.delpher.nl/nl/boeken/view?identifier={}'
    r = requests.get(url_template.format(row['delpher']))
    if r.status_code == 200:
        soup = BeautifulSoup(r.text)
        y = soup.find_all('h4', 'view-subtitle')
        if len(y) == 1:
            #print y[0].string
            year = y[0].string
            year = year.replace('XX', '50')
            year = year.replace('X', '0')
            return year
    return 'unknown'


selected = pd.read_excel('/home/jvdzwaan/Downloads/edbo.xlsx', 'Toneelstukken',
                         index_col=0, header=None, parse_cols=[1, 5],
                         names=['id', 'title'])

title_id2file_id = pd.read_csv('/home/jvdzwaan/Downloads/FROG/000README',
                               sep='\t', header=None, skiprows=11,
                               names=['file', 'delpher', 'genre'])

# add column with file id
title_id2file_id.loc[:, 'file_id'] = title_id2file_id.apply(get_file_id, axis=1)

# add column with list id
title_id2file_id.loc[:, 'list_id'] = title_id2file_id.apply(get_delpher_id, axis=1)

# remove invalid rows
title_id2file_id = title_id2file_id.dropna()
title_id2file_id = title_id2file_id.set_index('list_id', verify_integrity=True)

# merge dataframes
result = pd.concat([selected, title_id2file_id], axis=1, join_axes=[selected.index])
result = result.dropna()

result.loc[:, 'file_name'] = result.apply(copy_file, axis=1)
result = result.dropna()

# add unknown metadata
result.loc[:, 'genre'] = result.apply(get_genre, axis=1)
result.loc[:, 'year'] = result.apply(get_year, axis=1)

# normalize title
result['title'] = result.apply(lambda row: row['title'].replace('\t', ' '),
                               axis=1)

result = result.set_index('file_name', verify_integrity=True)
# save edbo list
to_save = pd.concat([result['year'], result['genre'], result['title']], axis=1)

to_save.to_csv('/home/jvdzwaan/data/embem/corpus/edbo.csv', sep='\t',
               encoding='utf-8', header=None)

#print result
