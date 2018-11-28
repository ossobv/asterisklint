#!/bin/sh
url=${1:-http://localhost:8080/dialplan-check/}
file=${2:-../extensions.conf}
jsondialplan=$(jq -Rs . "$file")
curl -XPOST "$url" --data-raw '{"files":{"extensions.conf":'"$jsondialplan"'}}'
