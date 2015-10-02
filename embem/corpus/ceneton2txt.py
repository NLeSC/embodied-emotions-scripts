"""Script to collect ceneton texts from the ceneton website.

Usage: python ceneton2txt.py <ceneton list xml file> <output dir>
"""
import argparse
import pandas as pd
import requests
from bs4 import BeautifulSoup
import codecs
import os
import re


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file_in', help='the name of the xlsx file with the '
                        'selected ceneton titles '
                        '(<embem_data_dir>/corpus/ceneton.xlsx)')
    parser.add_argument('dir_out', help='the name of the output directory')
    args = parser.parse_args()

    file_name = args.file_in
    out_dir = args.dir_out

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    titles = pd.read_excel(file_name)
    urls = titles['url'].str.startswith('http://')

    for row in enumerate(titles[urls].values):
        url = row[1][0]
        m = re.search(r'/(\w+\d{4})\w?\.html', url)
        if not m:
            print url
        else:
            fname = m.group(1)
            fname = fname.replace('.html', '')
            out_text = os.path.join(out_dir, '{}.txt'.format(fname))

            with codecs.open(out_text, 'wb', 'utf8') as f:
                f.write(url + '\n')

                result = requests.get(url)
                if result.status_code != 200:
                    f.write('Failed to get text\n')
                else:
                    # fix strange html entities
                    txt = result.text.replace('&#146;', "'")
                    txt = txt.replace('&#151;', "-")
                    txt = txt.replace('&#148;', '"')
                    soup = BeautifulSoup(txt)
                    f.write(soup.get_text())
