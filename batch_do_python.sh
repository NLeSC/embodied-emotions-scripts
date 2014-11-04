#!/bin/bash
# Run a python script for all files in a directory 
# Usage: ./batch_add_liwc_entities.sh <name of the python script that should
#be run> <dir with input-files> <dir to save output-files in> 
# 2014-11-04 j.vanderzwaan@esciencecenter.nl

echo ''
echo 'Running script:' $1
echo 'for all files in:' $2
echo 'saving output files in:' $3
echo ''

# Create output directory if it doesn't exist  
[[ -d "$3" ]] || mkdir "$3"

total=0

shopt -s nullglob
for in_file in $(find $2 -maxdepth 1 -type f); do
    total=$((total+1))
    
    echo "(${total}) ${in_file}"
    
    python $1 $in_file $3
done
