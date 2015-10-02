#!/bin/bash
# Copy folia files for texts in corpus.csv to a new directory.
#
# Usage: ./copy_corpus.sh.sh <corpus.csv> <dir with folia-files> <dir to copy
# folia files to>
#
# The first 13 characters in the corpus.csv file should be the text id. 
#
# 20150210 j.vanderzwaan@esciencecenter.nl 

echo ''
echo 'Copy folia files'
echo 'Reading corpus from' $1
echo 'Using FoLiA XML files in' $2
echo 'Copying FoLiA XML files to' $3
echo ''


# Create output directory if it doesn't exist  
[[ -d "$3" ]] || mkdir "$3"

while read line
do
    text_id=${line:0:13}
    for folia in $(find "$2/${text_id}_01.xml" -maxdepth 1 -type f); do
        echo $folia
        cp "$folia" "$3/."
    done
done < $1
