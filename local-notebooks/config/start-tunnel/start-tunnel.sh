#!/bin/bash

# This script downloads and installs an executable for an anonymous Cloudflare
# tunnel, and then starts the tunnel pointed to a local endpoint specified below.
# The public URL for the tunnel is printed in the logs -- it's different each time.

LOCAL_ENDPOINT=http://127.0.0.1:8888

DOWNLOAD_URL=https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
TUNNEL_EXE=~/opt/cloudflared

if [ ! -e "$TUNNEL_EXE" ]
then
	DIR=$(dirname $TUNNEL_EXE)
	mkdir -p "$DIR"
	curl -o $TUNNEL_EXE -L $DOWNLOAD_URL
	chmod u+x $TUNNEL_EXE
fi

$TUNNEL_EXE tunnel -url $LOCAL_ENDPOINT

