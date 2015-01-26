"""Helper functions to create dictionaries (lexicons).
"""
import codecs


def load_liwc(dict_file, encoding):

    with codecs.open(dict_file, 'rb', encoding) as f:
        lines = f.readlines()

    liwc_categories = {}
    liwc_dict = {}

    for line in lines:
        # LIWC category
        if line[0].isdigit():
            entry = line.split()
            # remove 0 from strings like 01
            c = str(int(entry[0]))
            liwc_categories[c] = entry[1]
        # word
        elif line[0].isalpha():
            entry = line.split()
            term = entry[0]
            categories = entry[1:]
            liwc_dict[term] = categories
    return liwc_dict, liwc_categories


