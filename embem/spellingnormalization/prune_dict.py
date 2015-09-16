"""Remove words in modern spelling from the spelling variants.
"""
import argparse
import codecs
import json

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dict', help='the name of the json file '
                        'containing the modern->spelling variants dictionary')
    parser.add_argument('output_dict', help='the name of the pruned '
                        'modern->spelling variants json dictionary')
    args = parser.parse_args()

    dict_file = args.input_dict
    dict_out = args.output_dict

    modern_dict = {}
    pruned_dict = {}

    with codecs.open(dict_file, 'rb', 'utf8') as f:
        modern_dict = json.load(f, encoding='utf-8')

    for modern_word, variants in modern_dict.iteritems():
        variants.remove(modern_word)
        if len(variants) > 0:
            pruned_dict[modern_word] = variants

    print '#words in modern dict: {}'.format(len(modern_dict))
    print '#words in pruned dict: {}'.format(len(pruned_dict))

    # save historic dictionary
    with codecs.open(dict_out, 'wb', 'utf8') as f:
        json.dump(pruned_dict, f, sort_keys=True, ensure_ascii=False,
                  indent=2)
