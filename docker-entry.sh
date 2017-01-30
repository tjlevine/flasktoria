#!/usr/bin/env bash

# set up socks proxy to the bastion node in background
ssh -fN -i /keys/docker-user.pem \
-o StrictHostKeyChecking=no \
-A -D 49797 \
docker-user@54.174.246.61

# give time for the first ssh connection to be established
sleep 2

# setup tunnel to the kafka node
ssh -fN -i /keys/docker-user.pem \
-o ExitOnForwardFailure=yes \
-o StrictHostKeyChecking=no \
-o ProxyCommand='nc -X 5 -x localhost:49797 %h %p' \
-L 9092:10.0.1.214:9092 \
-L 2181:10.0.1.214:2181 \
docker-user@10.0.1.214

# start the app
cd /flasktoria
python3 app.py