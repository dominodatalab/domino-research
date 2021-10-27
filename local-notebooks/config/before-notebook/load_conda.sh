#!/bin/bash 

# Init Conda
CONDA_BASE=$(/opt/conda/bin/conda info --base)
CONDA_FUNCTION="etc/profile.d/conda.sh"
CONDA="$CONDA_BASE/$CONDA_FUNCTION"
source $CONDA

# Find more recent backup file
BACKUP_PREFIX="/mnt/home/conda_backups"
BACKUP_FOLDER=$(ls $BACKUP_PREFIX | sort -r | head -n 1)

echo "Using environment backups from $BACKUP_FOLDER"

ENVS=$(ls $BACKUP_PREFIX/$BACKUP_FOLDER)
for env in $ENVS; do
    NAME="$(basename $env .yml)"
    echo "Env loading: $NAME"
    conda env update --name $NAME --file $BACKUP_PREFIX/$BACKUP_FOLDER/$env --prune >>/dev/null
    echo "Env loaded: $NAME"
done
