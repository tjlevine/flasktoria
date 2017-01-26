#!/usr/bin/env bash

# add required ssh config
mkdir ~/.ssh
echo "Host 10.0.1.*
    ProxyCommand nc -X 5 -x localhost:49797 %h %p" > ~/.ssh/config

# set up socks proxy to the bastion node in background
ssh -fN -i /keys/pnda-user.pem \
-o StrictHostKeyChecking=no \
-A -D 49797 \
ubuntu@54.174.246.61

# give time for the first ssh connection to be established
sleep 2

# setup tunnel to the kafka node
ssh -fN -i /keys/pnda-user.pem \
-o ExitOnForwardFailure=yes \
-o StrictHostKeyChecking=no \
-L 9092:10.0.1.214:9092 \
-L 2181:10.0.1.214:2181 \
ubuntu@10.0.1.214

# start the app
python3 app.py