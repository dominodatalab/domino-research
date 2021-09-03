#!/bin/bash
SCRIPT_DIR=$(cd $(dirname "$0"); pwd)
docker kill envoy || true
docker rm envoy || true
docker run --rm -d -p 10000:10000 --name envoy envoyproxy/envoy:v1.18.2 --config-yaml "$(cat config_mac.yaml)"
