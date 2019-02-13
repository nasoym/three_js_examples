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

  if which timeout >/dev/null ; then
    timeout_cmd="timeout"
  elif which gtimeout >/dev/null ; then
    timeout_cmd="gtimeout"
  fi

while getopts "a:h?" options; do case $options in
  a) a="$OPTARG" ;;
  h|?) help; exit ;;
esac; done; shift $((OPTIND - 1))

if [[ "$#" -eq 0 ]];then
  ${0} help

elif [[ "$1" == "help" ]];then shift
  which bash_scripts >/dev/null && bash_scripts show_commands ${0} || true

elif [[ "$1" == "bullet" ]];then shift
  docker rm -vf bullet || true
  docker run --name bullet -t -d --link rabbit -v ${self_path}/bullet_server.py:/pybullet_examples/bullet_server.py  nasoym/bullet_container python3 /pybullet_examples/bullet_server.py

elif [[ "$1" == "rabbit" ]];then shift
  docker rm -vf rabbit || true
  docker run --name rabbit -d -P --entrypoint "/bin/bash" rabbitmq:3-management -c 'rabbitmq-plugins enable --offline rabbitmq_web_stomp ;docker-entrypoint.sh rabbitmq-server'

elif [[ "$1" == "socat" ]];then shift
  docker rm -vf socat || true
  docker run --name socat -d --link rabbit -p 8080:8080 alpine /bin/sh -c "apk update; apk add socat; socat TCP-LISTEN:8080,fork TCP:rabbit:15674"

elif [[ "$1" == "queues" ]];then shift
  curl -i -s -XPUT --data-binary '{"auto_delete":false,"durable":false,"arguments":{}}' -u "guest:guest" "http://$(docker port rabbit 15672)/api/queues/%2F/foo"
  curl -i -s -XPUT --data-binary '{"auto_delete":false,"durable":true,"arguments":{}}' -u "guest:guest" "http://$(docker port rabbit 15672)/api/queues/%2F/updates"
  curl -i -s -XPUT --data-binary '{"auto_delete":false,"durable":false,"arguments":{}}' -u "guest:guest" "http://$(docker port rabbit 15672)/api/queues/%2F/commands"

elif [[ "$1" == "listen" ]];then shift
  rabbit_port="$(docker port rabbit 5672 | sed 's/.*://g')" python3 ${self_path}/python_pika_listen.py

elif [[ "$1" == "message" ]];then shift
  curl -i -s -XPOST --data-binary '{"properties":{},"routing_key":"foo","payload":"Hello World","payload_encoding":"string"}' -u "guest:guest" "http://$(docker port rabbit 15672)/api/exchanges/%2F//publish"

# elif [[ "$1" == "test" ]];then shift
#   curl -i -s \
#     -XPOST \
#     --data-binary '{"properties":{"content_type":"application/json"},"routing_key":"foo","payload":"[\"44-dkddkkddksjsldkjslkdf\"]","payload_encoding":"string"}' \
#     -u "guest:guest" \
#     "http://$(docker port rabbit 15672)/api/exchanges/%2F//publish"

# elif [[ "$1" == "test" ]];then shift
elif [[ "$1" == "json_to_queue" ]];then shift
#   echo '{"properties":{"content_type":"application/json"},"routing_key":"foo","payload":"[\"44-dkddkkddksjsldkjslkdf\"]","payload_encoding":"string"}' \
#   echo '{"properties":{"content_type":"application/json"},"routing_key":"foo","payload":"[\"44-dkddkkddksjsldkjslkdf\"]","payload_encoding":"string"}' \
#
#   jq -n '{properties:{content_type:"application/json"},routing_key:"foo",payload_encoding:"string",payload:.}'
#
# jq -c -n '{a:"44"}' 
  : ${routing_key:="commands"}
  : ${host:="$(docker port rabbit 15672)"}

  jq -c . \
  | jq --arg routing_key "${routing_key}" -R -c '{properties:{content_type:"application/json"},routing_key:$routing_key,payload_encoding:"string",payload:.}' \
  | curl -i -s \
    -XPOST \
    --data-binary @- \
    -u "guest:guest" \
    "http://${host}/api/exchanges/%2F//publish"

  # jq -c -n '{command:"create",id:2345}' \
  #   | jq -c -R '{properties:{},routing_key:"commands",payload:.,payload_encoding:"string"}' \
  #   | curl -i -s -XPOST --data-binary @- -u "guest:guest" "http://$(docker port rabbit 15672)/api/exchanges/%2F//publish"


elif [[ "$1" == "all" ]];then shift
  ${0} rabbit
  sleep 10
  ${0} socat
  ${timeout_cmd} 10 bash -c "until ${0} queues; do echo try again; sleep 1; done "
  ${0} bullet
  sleep 10
  jq --arg id "${RANDOM}" -c -n '{command:"create",shape:"box",id:$id}' \
    | ${0} json_to_queue
  jq --arg id "${RANDOM}" -c -n '{command:"create",shape:"box",id:$id}' \
    | ${0} json_to_queue

elif [[ "$1" == "clear" ]];then shift
  docker rm -vf socat || true
  docker rm -vf rabbit || true
  docker rm -vf bullet || true

elif [[ "$1" == "ec2_teardown" ]];then shift
  : ${ec2_host:="host"}
  ec2 ssh ${ec2_host} 'docker rm -vf rabbit || true'
  ec2 ssh ${ec2_host} 'docker rm -vf bullet || true'
  ec2 port-list | awk '{print $1}' | xargs --no-run-if-empty kill

elif [[ "$1" == "ec2_setup_rabbit" ]];then shift
  : ${ec2_host:="host"}
  # ec2 ssh ${ec2_host} "docker run --name rabbit -d -P --entrypoint '/bin/bash' rabbitmq:3-management -c 'rabbitmq-plugins enable --offline rabbitmq_web_stomp ;docker-entrypoint.sh rabbitmq-server'"

  ec2 ssh ${ec2_host} 'docker rm -vf rabbit || true'
  ec2 ssh ${ec2_host} "docker run --name rabbit -d -p 15672:15672 -p 15674:15674 activiti/rabbitmq-stomp"
  ${0} ec2_setup_rabbit_ports

elif [[ "$1" == "ec2_setup_rabbit_ports" ]];then shift
  : ${ec2_host:="host"}
  ec2 port ${ec2_host} 15672
  ec2 port ${ec2_host} 15674

elif [[ "$1" == "ec2_setup_bullet" ]];then shift
  : ${ec2_host:="host"}
  ec2 scp ${ec2_host} bullet_server.py bullet_server.py
  ec2 ssh ${ec2_host} 'docker rm -vf bullet || true'
  ec2 ssh ${ec2_host} 'docker run --name bullet -t -d --link rabbit -v $(pwd)/bullet_server.py:/pybullet_examples/bullet_server.py  nasoym/bullet_container python3 /pybullet_examples/bullet_server.py'

else
  echo "unknown command: $@" >&2
  exit 1
fi

