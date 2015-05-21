"""Print table with # of texts per genre and period
Based on csv file with corpus information

Usage: python genre2period.py <file in>
"""
import argparse
import codecs
from collections import Counter


def get_time_period(year):
    if not year == 'unknown':
        year = int(year)
        if year >= 1600 and year < 1670:
            return 'renaissance'
        elif year >= 1670 and year < 1750:
            return 'classisism'
        elif year >= 1750 and year <= 1830:
            return 'enlightenment'
    return None


def print_results_line_period(genre, results):
    r = results.get('renaissance', {}).get(genre, 0)
    c = results.get('classisism', {}).get(genre, 0)
    e = results.get('enlightenment', {}).get(genre, 0)
    n = results.get(None, {}).get(genre, 0)
    return '{}\t{}\t{}\t{}\t{}\t{}'. \
           format(genre, r, c, e, n, sum([r, c, e, n]))


def print_results_line_year(genre, sorted_years, years):
    line = [str(years.get(y, {}).get(genre, 0)) for y in sorted_years]
    return '{}\t{}'.format(genre, '\t'.join(line))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='the name of the FoLiA XML file that '
                        'should be processed.')
    args = parser.parse_args()

    file_name = args.file

    text_id = file_name[-20:-7]

    result = {}
    years = {}
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

            year = parts[1]
            if year not in years.keys():
                years[year] = Counter()
            years[year][genre] += 1

            if not period:
                period_none_ids.append(parts[0])
            if genre == 'Anders':
                genre_other_ids.append(parts[0])

    sorted_years = sorted(years.keys())
    print 'Genre\t{}'.format('\t'.join(sorted_years))
    print print_results_line_year('tragedie/treurspel', sorted_years, years)
    print print_results_line_year('blijspel / komedie', sorted_years, years)
    print print_results_line_year('klucht', sorted_years, years)
    print print_results_line_year('Anders', sorted_years, years)
    print print_results_line_year('unknown', sorted_years, years)

    print
    print

    print 'Genre\tRenaissance\tClassisim\tEnlightenment\tNone'
    print print_results_line_period('tragedie/treurspel', result)
    print print_results_line_period('blijspel / komedie', result)
    print print_results_line_period('klucht', result)
    print print_results_line_period('Anders', result)
    print print_results_line_period('unknown', result)

    print
    print

    print 'No period:\n', '\n'.join(period_none_ids)
    print
    print 'Genre other:\n', '\n'.join(genre_other_ids)
