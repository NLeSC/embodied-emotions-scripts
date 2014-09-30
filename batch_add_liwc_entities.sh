#!/bin/bash
# Batch add LIWC entities to FoLiA files
# Usage: ./batch_add_liwc_entities.sh <dir with folia-files> <dir to save
# kaf-files in>
# 2014-09-30 j.vanderzwaan@esciencecenter.nl

echo ''
echo 'Adding LIWC entities for FoLiA XML files in' $1
echo 'Saving new FoLiA XML files in' $2
echo ''

# Create output directory if it doesn't exist  
[[ -d "$2" ]] || mkdir "$2"

total=0

shopt -s nullglob
for folia in $(find $1 -maxdepth 1 -type f); do
    total=$((total+1))
    
    echo "(${total}) ${folia}"
    
    python add_liwc_entities.py $folia $2
done
