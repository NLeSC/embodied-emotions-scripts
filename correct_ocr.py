import glob
from count_labels import load_data
from collections import Counter
from bs4 import BeautifulSoup
import codecs
from fuzzywuzzy import process


# create word list
words = Counter()

data_dir = '/home/jvdzwaan/data/embem/txt/corpus_annotation/'

files = glob.glob('{}*.txt'.format(data_dir))
for i, file_ in enumerate(files):
    #print i+1, file_
    X_data, Y_data = load_data(file_)
    for line in X_data:
        words.update([unicode(w.lower()) for w in line.decode('utf-8').split()[1:] if len(w) > 1])

print len(words.keys())
print words.most_common(10)

# load text to be corrected
text = '/home/jvdzwaan/Downloads/zip/ticcl.xml'

with codecs.open(text, 'r', 'utf8') as f:
    soup = BeautifulSoup(f, 'xml')

lines = soup.find_all('t')
for line in lines:
    if line.text:
        for w in line.text.split():
            repl, score = process.extractOne(w.lower(), words.keys())
            print w, repl, score
