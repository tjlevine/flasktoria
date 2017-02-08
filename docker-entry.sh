#!/usr/bin/env bash

# add the pnda-proxy container IP to /etc/hosts as pnda-clb-cluster-kafka-0
# so that the broker bootstrap process can complete successfully
ENT="10.0.1.214      pnda-clb-cluster-kafka-0"

if [ -z "$ENT" ]; then
    echo "Did not find address for pnda-proxy container, will not be able to connect to kafka"
else
    echo "Adding entry to /etc/hosts: $ENT"
    echo $ENT >> /etc/hosts
fi

# start the app
cd /flasktoria
exec python3 app.py
