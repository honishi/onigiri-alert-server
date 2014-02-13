#!/usr/bin/env bash

set -e

basedir=$(cd $(dirname $0);pwd)

source ${basedir}/push.env

curl -X POST \
  -H "X-Parse-Application-Id: ${APPLICATION_ID}" \
  -H "X-Parse-REST-API-Key: ${REST_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
        "where": {
          "deviceType": "ios"
        },
        "data": {
          "alert": "テストアラートです."
        }
      }' \
  https://api.parse.com/1/push
