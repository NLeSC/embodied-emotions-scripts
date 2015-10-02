#!/usr/bin/env python
# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch, helpers
from collections import Counter
from datetime import datetime


def find_pairs(list1, list2):
    pairs = []
    if list1 and list2:
        for item1 in list1:
            for item2 in list2:
                pairs.append(u'{}@{}'.format(item1, item2))
    return pairs


es = Elasticsearch()
index_name = 'embem'
doc_type = 'event'
cat1 = 'Body'
cat2 = 'Posemo'

timestamp = datetime.now().isoformat()

pairs_count = Counter()
years = {}

q = {
    "query": {
        "wildcard": {"text_id": "*"}
    }
}

results = helpers.scan(client=es, query=q, index=index_name, doc_type=doc_type)
for r in results:
    # get tags
    cat1_tags = r.get('_source').get('liwc-entities').get('data').get(cat1)
    cat2_tags = r.get('_source').get('liwc-entities').get('data').get(cat2)

    # find all pairs
    pairs = find_pairs(cat1_tags, cat2_tags)

    if pairs:
        for pair in pairs:
            pairs_count[pair] += 1
            year = r.get('_source').get('year')
            if year not in years.keys():
                years[year] = Counter()
            years[year][pair] += 1

    # save pairs to ES
    doc = {
        'doc': {
            'pairs-{}-{}'.format(cat1, cat2): {
                'data': pairs,
                'num_pairs': len(pairs),
                'timestamp': timestamp
            }
        }
    }
    es.update(index=index_name, doc_type=doc_type,
              id=r.get('_id'), body=doc)

sorted_years = years.keys()
sorted_years.sort()

print '{}\t{}\tFrequency'.format(cat1, cat2) + \
      ''.join(['\t{}'.format(k) for k in sorted_years])
print 'TOTAL\tTOTAL\t{}'.format(sum(pairs_count.values())) + \
      ''.join(['\t{}'.format(sum(years[k].values())) for k in sorted_years])
for p, f in pairs_count.most_common():
    (w1, w2) = p.split('@')
    print u'{}\t{}\t{}'.format(w1, w2, f).encode('utf-8') + \
          ''.join(['\t{}'.format(years[k][p]) for k in sorted_years])
