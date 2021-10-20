#!/bin/bash
set -ex
mkdir -p /mnt/home

# Configure S3FS
mkdir -p /tmp/s3fs

if [[ -z "${DEPLOY_ENV}" ]]; then
    echo "Obtained credentials from environment"
    echo "${AWS_ACCESS_KEY_ID}:${AWS_SECRET_ACCESS_KEY}" > /root/.passwd-s3fs
    chmod 600 /root/.passwd-s3fs
fi
sudo s3fs kevin-notebook-test:/team-id /mnt/home -o allow_other -o use_cache=/tmp/s3fs
