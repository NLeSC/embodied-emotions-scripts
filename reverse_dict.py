"""Reverse modern->historic spelling variants dictonary to historic->modern
mappings
"""
import argparse
import codecs
import json
from collections import Counter

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dict', help='the name of the json file '
                        'containing the modern->spelling variants dictionary')
    parser.add_argument('output_dict', help='the name of the json file '
                        'to save the historic->modern dictionary to')
    args = parser.parse_args()

    dict_file = args.input_dict
    dict_out = args.output_dict

    modern_dict = {}
    historic_dict = {}

    with codecs.open(dict_file, 'rb', 'utf8') as f:
        modern_dict = json.load(f, encoding='utf-8')

    for modern_word, variants in modern_dict.iteritems():
        for var in variants:
            if var != modern_word:
                if var not in historic_dict.keys():
                    historic_dict[var] = Counter()
                historic_dict[var][modern_word] += 1

    print '#words in modern dict: {}'.format(len(modern_dict))
    print '#words in historic dict: {}'.format(len(historic_dict))

    # save historic dictionary
    with codecs.open(dict_out, 'wb', 'utf8') as f:
        json.dump(historic_dict, f, sort_keys=True, ensure_ascii=False,
                  indent=2)

    # find historic words that map to mulitple terms
    mappings_counter = Counter()

    print '\nhistoric words that map to mulitple modern words'
    print 'historic word\tmodern variant\tfrequency'

    for w, mappings in historic_dict.iteritems():
        mappings_counter[str(len(mappings)).zfill(3)] += 1
        if len(mappings) > 1:
            for variant, freq in mappings.iteritems():
                print '{}\t{}\t{}'.format(w.encode('utf-8'),
                                          variant.encode('utf-8'),
                                          freq)

    mp = mappings_counter.keys()
    mp.sort()
    print '\n#mappings\t#historic words'
    for m in mp:
        print '{}\t{}'.format(m.encode('utf-8'), mappings_counter[m])
