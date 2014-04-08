#!/usr/bin/env bash

set -e

basedir=$(cd $(dirname $0);pwd)
# envfile=${basedir}/push.env

# echo arguments count: $#
# exit

if ! [ $# -eq 2 -o $# -eq 3 ]; then
  echo "usage:   \$ $0 envfile channel [subchannel]"
  echo "example: \$ $0 ./push.env.dev ts02"
  echo "         \$ $0 ./push.env.dev ts02 user1"
  exit 1
fi

# envfile, channel, subchannel

envfile=${1}
channel=${2}
subchannel=${3:-""}

echo "-----"
echo "envfile:    ${envfile}"
echo "channel:    ${channel}"
echo "subchannel: ${subchannel}"

# where

where="\"channels\": \"${channel}\""
if [ ! -z ${subchannel} ]; then
  where="${where}, \"subChannels\": \"${subchannel}\""
fi

echo "-----"
echo "where: ${where}"

# data

data="\"alert\": \"テストアラートです.\", \"sound\": \"horagai.aiff\""
if [ ! -z ${subchannel} ]; then
  data="${data}, \"username\": \"${subchannel}\""
fi

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
          ${data}
        },
        \"expiration_time\": ${expire_time}
      }" \
  https://api.parse.com/1/push
