#!/bin/bash
# Batch fix word ids in the tag-files
# 'Translates' lg-added ids into proper folia word ids using the fix_tags
# python script.
#
# Usage: ./batch_fix_tags.sh <dir with folia-files> <dir with tag-files dirs>
# <dir to save new tag-files in>
#
# Tag files for a folia file should be in a directory named text_id.
#
# 20141209 j.vanderzwaan@esciencecenter.nl

echo ''
echo 'Fix tag files'
echo 'Using FoLiA XML files in' $1
echo 'Reading tag files from' $2
echo 'Saving new tag files in' $3
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
    folia="$1/$xml_name"

    # Does the folia file exist?
    # The text id (and thus the folia file name) comes from the directory
    # containing the tag files. Sometimes this directory has been renamed.
    if [ -e "$folia" ]; then

        # tag files are saved to a directory with the text_id
        output_dir="$3/$text_id"
        [[ -d "$output_dir" ]] || mkdir "$output_dir"

        for tag in $(find $2/$text_id -maxdepth 1 -type f); do
            if [[ $tag == *.tag ]]; then
                echo " $tag"
                python embem/kaf-tag/fix_tags.py $folia $tag "$output_dir" 
            fi
        done

    else
        echo "$folia_old does not exist. Please rename $dir to the "
        echo "correct text id."
    fi

done
