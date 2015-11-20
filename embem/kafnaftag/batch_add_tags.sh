#!/bin/bash
# Batch add annotations in tag files to FoLiA files
# Usage: ./batch_add_tags.sh <dir with folia-files> <dir with tag-files dirs>
# <dir to save new folia-files in>
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
for dir in $(find $2 -mindepth 1 -maxdepth 1 -type d); do
    total=$((total+1))

    text_id=${dir:(-13)}
    echo "(${total}) ${text_id}"

    xml_name="${text_id}_01.xml"
    folia_old="$1/$xml_name"
    folia_new="$3/$xml_name"

    # Does the folia file exist?
    # The text id (and thus the folia file name) comes from the directory
    # containing the tag files. Sometimes this directory has been renamed.
    if [ -e "$folia_old" ]; then
        # copy xml file to destination, because if there are multple tag files for
        # a folia file, the output is written to file for every tag file (to avoid
        # flooding the memory)
        cp $folia_old $folia_new

        for tag in $(find $2/$text_id -maxdepth 1 -type f); do
            if [[ $tag == *.tag ]]; then
                echo " $tag"
                python embem/kaf-tag/kaf2folia.py $tag $folia_new 
            fi
        done

    else
        echo "$folia_old does not exist. Please rename $dir to the "
        echo "correct text id."
    fi

done
