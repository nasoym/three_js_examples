#!/usr/bin/env bash
set -o errexit  # abort when any commands exits with error
set -o pipefail # abort when any command in a pipe exits with error
set -o nounset  # abort when any unset variable is used
set -o noglob # prevent bash from expanding glob
set -o errtrace # inherits trap on ERR in function and subshell
if [[ "${trace:=0}" -eq 1 ]];then
  PS4=' ${LINENO}: '
  set -x
  export trace
fi
trap 'status="$?"; echo "$(basename $0): status:${status} LINENO:${LINENO} BASH_LINENO:${BASH_LINENO} command:${BASH_COMMAND} functions:$(printf " %s" ${FUNCNAME[@]:-})"; exit ${status}' ERR

self="$(cd $(dirname "${BASH_SOURCE[0]}") && pwd -P)/$(basename "$0")"
self_path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

while getopts "a:h?" options; do case $options in
  a) a="$OPTARG" ;;
  h|?) help; exit ;;
esac; done; shift $((OPTIND - 1))

if [[ "$#" -eq 0 ]];then
  ${0} help

elif [[ "$1" == "help" ]];then shift
  which bash_scripts >/dev/null && bash_scripts show_commands ${0} || true

elif [[ "$1" == "rabbit" ]];then shift
  docker run --name rabbit -d  -P --entrypoint "/bin/bash" rabbitmq:3-management -c 'rabbitmq-plugins enable --offline rabbitmq_web_stomp ;docker-entrypoint.sh rabbitmq-server'

elif [[ "$1" == "socat" ]];then shift
  docker run --name socat -d --link rabbit -p 8080:8080 alpine /bin/sh -c "apk update; apk add socat; socat TCP-LISTEN:8080,fork TCP:rabbit:15674"

elif [[ "$1" == "create_queue" ]];then shift
  curl -i -s -XPUT --data-binary '{"auto_delete":false,"durable":true,"arguments":{}}' -u "guest:guest" "http://$(docker port rabbit 15672)/api/queues/%2F/foo"

elif [[ "$1" == "message" ]];then shift
  curl -i -s -XPOST --data-binary '{"properties":{},"routing_key":"foo","payload":"Hello World","payload_encoding":"string"}' -u "guest:guest" "http://$(docker port rabbit 15672)/api/exchanges/%2F//publish"

# elif [[ "$1" == "test" ]];then shift
#   curl -i -s \
#     -XPOST \
#     --data-binary '{"properties":{"content_type":"application/json"},"routing_key":"foo","payload":"[\"44-dkddkkddksjsldkjslkdf\"]","payload_encoding":"string"}' \
#     -u "guest:guest" \
#     "http://$(docker port rabbit 15672)/api/exchanges/%2F//publish"

elif [[ "$1" == "test" ]];then shift
#   echo '{"properties":{"content_type":"application/json"},"routing_key":"foo","payload":"[\"44-dkddkkddksjsldkjslkdf\"]","payload_encoding":"string"}' \
#   echo '{"properties":{"content_type":"application/json"},"routing_key":"foo","payload":"[\"44-dkddkkddksjsldkjslkdf\"]","payload_encoding":"string"}' \
#
#   jq -n '{properties:{content_type:"application/json"},routing_key:"foo",payload_encoding:"string",payload:.}'
#
# jq -c -n '{a:"44"}' 
  jq -c . \
  | jq -R -c '{properties:{content_type:"application/json"},routing_key:"foo",payload_encoding:"string",payload:.}' \
  | curl -i -s \
    -XPOST \
    --data-binary @- \
    -u "guest:guest" \
    "http://$(docker port rabbit 15672)/api/exchanges/%2F//publish"

elif [[ "$1" == "all" ]];then shift
  docker rm -vf rabbit socat || true
  ${0} rabbit
  ${0} socat
  sleep 20
  ${0} create_queue
  sleep 5
  browser_open_url ${self_path}/test2.html
  ${0} message

else
  echo "unknown command: $@" >&2
  exit 1
fi

