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

Scripts to do things with Elasticsearch.

`embem-tags2es.py` -> Script to put embodied emotions entity categories in elasticsearch  
`folia2es.py` -> Script to put a folia xml file in ElasticSearch  
`liwc2es.py` -> Script to put liwc entity categories in elasticsearch  
`liwcpairs2es.py` -> Script to put Body/Posemo pairs in elasticsearch (does not work, because there are no folia files that contain liwc entities in the data dir. _The script also seems unfinished, because it only creates pairs for Posemo words._)

### Emotools

Helpers for the other scripts.
    
### Folia

Scripts to do things with folia files.

`add_liwc_entities.py` -> Add LIWC words as entities in FoLiA XML files
`batch_add_liwc_entities.sh` -> Batch add LIWC entities to FoLiA files (run from project directory)
`annotation_statistics.py` -> Count the numbers of annotated entities and emotional sentences in the corpus that was manually annotated. Prints tab separated data to std out.  
`folia2txt.py` -> Script to extract text from a folia xml file (use with batch_do_python.sh)  
`inspect_folia.py` -> Inspect FoLiA XML file to determine whether it matches our expectations (old, not used for project, because none of the files matched our expectations)

## Kaf-tag

Scripts to do things with kaf/tag files.

`generate_kaf.sh` -> Batch generate kaf-files from folia files (run from project directory)  
`folia2kaf.py` -> Create a KAF file for each act in a FoLiA file (used with `generate_kaf.sh`)  

Because for some reason, we used different folia files to generate the tag files and these folia files were  not available anymore, the tag files needed fixing.   
`batch_fix_tags.sh` -> Batch fix word ids in the tag-files (run from project directory)   
`fix_tags.py` -> Script that generates a tag file with new word ids

`batch_add_tags.sh` -> Batch add annotations in tag files to FoLiA files (run from project directory)  
`kaf2folia.py` -> Insert KAF annotations into a FoLiA files (used with `batch_add_tags.sh`)