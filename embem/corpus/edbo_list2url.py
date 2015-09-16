"""Script to add delpher links to a list of edbo titles.

Usage: python edbo_list2url.py <list with edbo titles and delpher ids>
"""
import argparse
import pandas as pd
#import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file_in', help='the name of the list containing the '
                        'selected EDBO titles '
                        '(<embem_data_dir>/corpus/edbo.csv)')
    args = parser.parse_args()

    file_name = args.file_in

    titles = pd.read_csv(file_name, sep='\t', header=None,
                         names=['ceneton_id', 'delpher_id', 'genre'])

    url_template = 'http://www.delpher.nl/nl/boeken/view?identifier={}'
    titles['url'] = pd.Series([url_template.format(id)
                               for id in titles['delpher_id']])

    #excel_name, _ = os.path.splitext(file_name)
    #titles.to_excel(pd.ExcelWriter('{}.xlsx'.format(excel_name)))
    titles.to_csv(file_name, sep='\t')
