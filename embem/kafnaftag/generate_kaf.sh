#!/bin/bash
# Batch generate kaf-files from folia files
# Usage: ./generate_kaf.sh <dir with folia-files> <dir to save kaf-files in>
# Disabled checking of folia files
# 2014-09-10 j.vanderzwaan@esciencecenter.nl

echo ''
echo 'Generating kaf-files for FoLiA XML files in' $1
echo 'Saving kaf-files in' $2
echo ''

# Create output directory if it doesn't exist
[[ -d "$2" ]] || mkdir "$2"

total=0
invalid=0
valid=0

# create temp file to store error reports
touch /tmp/folia2kaf

shopt -s nullglob
for folia in $(find $1 -maxdepth 1 -type f); do
    total=$((total+1))

    echo "(${total}) ${folia}"

    # extract play id
    # example file name: /home/jvdzwaan/data/test_embem/feit007patr01_01.xml
    # extract 13 characters 20 characters from the end of the string
    play_id=${folia:(-20):13}

    # check folia file
    #echo "Checking FoLiA XML..."
    #python inspect_folia.py $folia > /tmp/folia2kaf
    #folia_ok=$?
    folia_ok=0

    if [ $folia_ok -eq 0 ];then
        valid=$((valid+1))
        echo "Generating kaf-files..."

        # create directory for play
        play_dir="${2}/${play_id}"
        [[ -d "$play_dir" ]] || mkdir "$play_dir"

        python embem/kaf-tag/folia2kaf.py $folia $play_dir > /dev/null

        # download pdf file
        echo "Downloading pdf file..."
        wget "http://dbnl.nl/tekst/${play_id}_01/${play_id}_01.pdf" -O "${play_dir}/${play_id}.pdf"
    else
        invalid=$((invalid+1))
        echo "Invalid FoLiA file."

        # write id to text file
        error_dir="${2}/invalid"
        [[ -d "$error_dir" ]] || mkdir "$error_dir"

        error_ids_file="${error_dir}/ids.txt"
        touch $error_ids_file
        echo $play_id >> $error_ids_file

        # write error report to text file
        error_report_file="${error_dir}/${play_id}.txt"
        cat /tmp/folia2kaf > $error_report_file
    fi
    echo ''
done

rm /tmp/folia2kaf

echo "Total: ${total} Valid: ${valid} Invalid: ${invalid}"
