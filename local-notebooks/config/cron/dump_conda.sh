#!/bin/bash

# modified from: https://github.com/conda/conda/issues/5165#issuecomment-665354035

# Init Conda
CONDA_BASE=$(/opt/conda/bin/conda info --base)
CONDA_FUNCTION="etc/profile.d/conda.sh"
CONDA="$CONDA_BASE/$CONDA_FUNCTION"
source $CONDA

# Create backup file
NOW=$(date "+%Y%m%d%H%M%S")
LOC=/mnt/home/conda_backups/$NOW
mkdir -p $LOC

ENVS=$(conda env list | grep '^\w' | cut -d' ' -f1)
for env in $ENVS; do
    echo "Exporting $env"
    conda activate $env
    conda env export > $LOC/$env.yml
done
