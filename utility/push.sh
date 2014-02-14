#!/usr/bin/env bash

set -e

basedir=$(cd $(dirname $0);pwd)
envfile=${basedir}/push.env

if [ $# -eq 1 ]; then
  envfile=${1}
fi

echo using envfile ${envfile}
source ${envfile}

curl -X POST \
  -H "X-Parse-Application-Id: ${APPLICATION_ID}" \
  -H "X-Parse-REST-API-Key: ${REST_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
        "where": {
          "deviceType": "ios"
        },
        "data": {
          "alert": "テストアラートです.",
          "sound": "horagai.aiff"
        }
      }' \
  https://api.parse.com/1/push
