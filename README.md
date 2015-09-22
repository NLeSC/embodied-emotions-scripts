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

### Kaf-tag

Scripts to do things with kaf/tag files.

`generate_kaf.sh` -> Batch generate kaf-files from folia files (run from project directory)  
`folia2kaf.py` -> Create a KAF file for each act in a FoLiA file (used with `generate_kaf.sh`)  

Because for some reason, we used different folia files to generate the tag files and these folia files were  not available anymore, the tag files needed fixing.
`batch_fix_tags.sh` -> Batch fix word ids in the tag-files (run from project directory)
`fix_tags.py` -> Script that generates a tag file with new word ids

`batch_add_tags.sh` -> Batch add annotations in tag files to FoLiA files (run from project directory)  
`kaf2folia.py` -> Insert KAF annotations into a FoLiA files (used with `batch_add_tags.sh`)

### LIWC

`print_liwc_cat.py` -> Script to print all words in a LIWC category to std out  
`liwc2csv.py` -> Script to generate statistics on LIWC entities for each folia file in a directory  

### Machine Learning

`br_classifier.py` -> Script to train binary relevance classifiers  
`do_br.sh` -> Bash script to run all br experiments  
`rakel_clf.py` -> Script to train rakel classifiers  
`do_rakel.sh` -> Bash script to run all rakel experiments  
`rakel.py` -> Class to create RAKEL classifier  
`rakel_save_clf.py` -> Script to train rakel classifier (based on all data) and save classifier object  
`classify.py` -> Script to classify new data  
`mlutils.py` -> Utils for the machine learning scripts

### Machine Learning Data

Contains scripts to generate input for machine learning (training classifiers) and scripts to generate results based on the output of machine learning.

#### Input

`folia2dataset_multilabel.py` -> Create multilabel data set to train embodied emotions classifiers (sentences with labels)  
`folia2dataset_emo_sentences.py` -> Create data set to train emotional sentence classifier (sentence with 0 or 1)  
`folia2dataset_for_prediction.py` -> Create text files for prediction (sentences with None)  
`create_multilabel_train_and_test_set.py` -> Create 10 different train and test sets (used for determining classifier performance)  
`generate_labels_json.py` -> Generate json objects storing the label replacements for diffent subdivisions of the emotion labels  
`transform_labels.py` -> Generate text files with transformed labels (e.g., HEEM -> HEEM emotion clusters)   
`txt2for_prediction.py` -> Script to convert text file to input for embem classifier    
`merge_data_and_labels.py` -> Merge sentences from one file to HEEM labels in another

#### Output 

`label_density.py` -> Calculate label density and cardinality of the complete dataset
`count_labels.py` -> Script to write csv file with label counts for each text  
`count_labelsets.py` -> Count labelsets that occur in the multilabel data  
`calculate_significance.py` -> Script that calculates statistical significance between two experiments  
`calculate_average_f1.py` -> Script that calculates average F1 scores for all labels  

### Embem

Other scripts.

`heem2csv.py` -> Count the numbers of words annotated with heem entities in the annotation corpus
`translate_labels.py` -> Translate Dutch HEEM labels to English  
