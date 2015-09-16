# Embodied Emotions Scripts

## Installation

## Code

Code is in de `embem` directory.

### Body parts

`make_body_part_mapping.py` -> Make a mapping from body part words to categories (extended body parts)  
`classify_body_parts.py` -> Find known body parts in sentences with predicted label 'Lichaamsdeel'

### Corpus

`ceneton2txt.py` -> Script to collect ceneton texts from the ceneton website  
`copy_corpus.sh` -> Copy folia files for texts in corpus.csv to a new directory  
`copy_edbo_titles.py` -> Script that copies the files of edbo titles that are both available and selected (contains hard-coded file paths for convenience)  
`create_additional_metadata.py` -> Script to create a csv containing additional metadata about corpus texts  
`edbo_list2url.py` -> Script to add delpher links to a list of edbo titles  
`genre2period.py` -> Print table with # of texts per genre and period

### Debates

Scripts used during the guest lecture at the VU on December 1, 2014.

`debates2csv.py` -> Script to extract counts for words in word field
`debates2txt.py` -> Script to save text in xml file(s) to text file(s)

### Elasticsearch

`embem-tags2es.py` -> Script to put embodied emotions entity categories in elasticsearch  
`folia2es.py` -> Script to put a folia xml file in ElasticSearch  
`liwc2es.py` -> Script to put liwc entity categories in elasticsearch  
`liwcpairs2es.py` -> Script to put Body/Posemo pairs in elasticsearch (does not work, because there are no folia files that contain liwc entities in the data dir. _The script also seems unfinished, because it only creates pairs for Posemo words._)

### 
    
### Folia

Scripts to do things with folia files.

* 
