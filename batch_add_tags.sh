#!/bin/bash
# Batch add annotations in tag files to FoLiA files
# Usage: ./batch_add_tags.sh <dir with folia-files> <dir with tag-files dirs>
# <dir to save kaf-files in>
# Tag files for a folia file should be in a directory named text_id. 
# 2014-11-04 j.vanderzwaan@esciencecenter.nl

echo ''
echo 'Adding tags for FoLiA XML files in' $1
echo 'Reading tag files from' $2
echo 'Saving new FoLiA XML files in' $3
echo ''

# Create output directory if it doesn't exist  
[[ -d "$3" ]] || mkdir "$3"

total=0

shopt -s nullglob
for folia in $(find $1 -maxdepth 1 -type f); do
    total=$((total+1))
    
    echo "(${total}) ${folia}"

    text_id=${folia:(-20):(-7)}
    xml_name=${folia:(-20)}

    echo "$text_id $xml_name"
    
    # copy xml file to destination, because if there are multple tag files for
    # a folia file, the output is written to file for every tag file (to avoid
    # flooding the memory)
    cp $folia $3/$xml_name

    for tag in $(find $2/$text_id -maxdepth 1 -type f); do
        echo " $tag"
        python kaf2folia.py $tag $folia 
    done
done
