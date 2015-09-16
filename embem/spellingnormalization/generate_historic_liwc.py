#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import sleep
import json
import codecs
from emotools.lexicon import get_spelling_variants


if __name__ == '__main__':
    # read file and convert byte strings to unicode
    with codecs.open('LIWC_Dutch_dictionary.dic', 'rb', 'latin-1') as f:
        lines = f.readlines()

    liwc_category_output = []
    spelling_vars = {}
    liwc_output = {}
    for line in lines:
        # legend
        if line[0].isdigit() or line.startswith(('%', '\r')):
            liwc_category_output.append(line.strip())
        # word
        else:
            entry = line.split()
            # lexicon service needs lower case input
            term = entry[0].lower()
            categories = entry[1:]
            sleep(0.3)
            words = get_spelling_variants(term, categories, 1600, 1830)
            words.append(term)
            words = list(set(words))

            spelling_vars[term] = words

            print term, words
            for word in words:
                if liwc_output.get(word) and not categories == liwc_output[word]:
                    new_c = list(set(categories + liwc_output.get(word)))
                    new_c.sort()
                    liwc_output[word] = new_c
                else:
                    liwc_output[word] = categories
    #with codecs.open('liwc_output.json', 'w', 'utf8') as f:
    #    json.dump(liwc_output, f, sort_keys=True, ensure_ascii=False, indent=2)

    #with codecs.open('liwc_output.json', 'rb', 'utf8') as f:
    #    liwc_output = json.load(f, encoding='utf-8')

    # write spelling variants to file
    with codecs.open('liwc_spelling_variants.json', 'w', 'utf8') as f:
        json.dump(spelling_vars, f, sort_keys=True, ensure_ascii=False, indent=2)

    with codecs.open('historic_Dutch_LIWC.dic', 'wb', 'utf8') as f:
        f.write('\n'.join(liwc_category_output))

        entries = liwc_output.keys()
        entries.sort()
        for entry in entries:
            f.write(entry)
            f.write('\t\t')
            f.write('\t'.join(liwc_output[entry]))
            f.write('\n')
