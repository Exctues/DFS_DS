#!/bin/bash

cd docker
docker build -f namenode_dockerfile -t namenode --build-arg SSH_PRIVATE_KEY=/.ssh/id .