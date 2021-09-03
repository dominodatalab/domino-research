#!/bin/bash
SCRIPT_DIR=$(cd $(dirname "$0"); pwd)
docker kill envoy || true
docker rm envoy || true
docker run --rm -d --network host --name envoy envoyproxy/envoy:v1.18.2 --config-yaml "$(cat config.yaml)"
