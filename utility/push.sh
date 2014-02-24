#!/usr/bin/env bash

set -e

basedir=$(cd $(dirname $0);pwd)
envfile=${basedir}/push.env

if [ $# -lt 1 ]; then
  echo "usage:   $0 channel_name [env_file]"
  echo "example: $0 ts02 ./push.env.dev"
  exit 1
fi

if [ $# -eq 2 ]; then
  envfile=${2}
fi

echo using envfile ${envfile}
source ${envfile}

current_time=$(date '+%s')
active_duration=$((60 * 60))  # = 1h
expire_time=$((${current_time} + ${active_duration}))

echo "current: ${current_time}"
echo "active:  ${active_duration}"
echo "expire:  ${expire_time}"

curl -X POST \
  -H "X-Parse-Application-Id: ${APPLICATION_ID}" \
  -H "X-Parse-REST-API-Key: ${REST_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
        \"channels\": [
          \"${1}\"
        ],
        \"data\": {
          \"alert\": \"テストアラートです.\",
          \"sound\": \"horagai.aiff\"
        },
        \"expiration_time\": ${expire_time}
      }" \
  https://api.parse.com/1/push
