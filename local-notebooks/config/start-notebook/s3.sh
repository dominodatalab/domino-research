#!/bin/bash
set -e

mkdir -p /mnt/home

# Configure S3FS
mkdir -p /tmp/s3fs

echo "$(cat /etc/aws/credentials | jq -r .AccessKey.AccessKeyId):$(cat /etc/aws/credentials | jq -r .AccessKey.SecretAccessKey)" > /etc/passwd-s3fs
chmod 600 /etc/passwd-s3fs

s3fs ${AWS_BUCKET} /mnt/home -o allow_other -o use_cache=/tmp/s3fs

echo "S3 Mounted"

sleep 1
