#!/usr/bin/env bash

# add the pnda-proxy container IP to /etc/hosts as pnda-clb-cluster-kafka-0
# so that the broker bootstrap process can complete successfully
ENT="10.0.1.214      pnda-clb-cluster-kafka-0"
ENT2="10.0.1.124      pnda-clb-cluster-cdh-dn-0"

echo "Adding entry to /etc/hosts: $ENT"
echo $ENT >> /etc/hosts
echo "Adding entry to /etc/hosts: $ENT2"
echo $ENT2 >> /etc/hosts

# start the app
cd /flasktoria
exec python3 app.py
