"""Print table with # of texts per genre and period
Based on csv file with corpus information

Usage: python genre2period.py <file in>
"""
import argparse
import codecs
from collections import Counter


def get_time_period(year):
    year = int(year)
    if year >= 1600 and year < 1660:
        return 'renaissance'
    elif year >= 1660 and year < 1750:
        return 'classisism'
    elif year >= 1750 and year <= 1830:
        return 'enlightenment'
    else:
        return None


def print_results_line(genre, results):
    return '{}\t{}\t{}\t{}\t{}'. \
           format(genre,
                  results.get('renaissance').get(genre, 0),
                  results.get('classisism').get(genre, 0),
                  results.get('enlightenment').get(genre, 0),
                  results.get(None, {}).get(genre, 0))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='the name of the FoLiA XML file that '
                        'should be processed.')
    args = parser.parse_args()

    file_name = args.file

    text_id = file_name[-20:-7]

    result = {}
    period_none_ids = []
    genre_other_ids = []

    # read text metadata
    with codecs.open(file_name, 'rb', 'utf8') as f:
        for line in f.readlines():
            parts = line.split('\t')
            period = get_time_period(parts[1])
            genre = parts[2]

            if period not in result.keys():
                result[period] = Counter()
            result[period][genre] += 1

            if not period:
                period_none_ids.append(parts[0])
            if genre == 'Anders':
                genre_other_ids.append(parts[0])

    print 'Genre\tRenaissance\tClassisim\tEnlightenment\tNone'
    print print_results_line('tragedie/treurspel', result)
    print print_results_line('blijspel / komedie', result)
    print print_results_line('klucht', result)
    print print_results_line('Anders', result)

    print
    print

    print 'No period:\n', '\n'.join(period_none_ids)
    print
    print 'Genre other:\n', '\n'.join(genre_other_ids)
