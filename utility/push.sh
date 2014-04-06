#!/usr/bin/env bash

set -e

basedir=$(cd $(dirname $0);pwd)
# envfile=${basedir}/push.env

# echo arguments count: $#
# exit

if ! [ $# -eq 2 -o $# -eq 3 ]; then
  echo "usage:   \$ $0 envfile channel [subuser]"
  echo "example: \$ $0 ./push.env.dev ts02"
  echo "         \$ $0 ./push.env.dev ts02 user1"
  exit 1
fi

# envfile, channel, subuser

envfile=${1}
channel=${2}
subuser=${3:-""}

# if [ $# -eq 3 ]; then
#   subuser=", \"${3}\": true"
# fi

echo "-----"
echo "envfile: ${envfile}"
echo "channel: ${channel}"
echo "subuser: ${subuser}"

# where

where="\"channels\": \"${channel}\""

if [ ! -z ${subuser} ]; then
  where="${where}, \"${3}\": true"
fi

echo "-----"
echo "where: ${where}"

# expire time

current_time=$(date '+%s')
active_duration=$((60 * 60))  # = 1h
expire_time=$((${current_time} + ${active_duration}))

echo "-----"
echo "current: ${current_time}"
echo "active:  ${active_duration}"
echo "expire:  ${expire_time}"

echo "-----"

source ${envfile}

curl -X POST \
  -H "X-Parse-Application-Id: ${APPLICATION_ID}" \
  -H "X-Parse-REST-API-Key: ${REST_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
        \"where\": { 
          ${where}
        },
        \"data\": {
          \"alert\": \"テストアラートです.\",
          \"sound\": \"horagai.aiff\"
        },
        \"expiration_time\": ${expire_time}
      }" \
  https://api.parse.com/1/push
