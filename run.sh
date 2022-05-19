#!/bin/bash
cd /home/ubuntu/spring-boot-mongo
docker-compose build --no-cache
docker-compose up -d
