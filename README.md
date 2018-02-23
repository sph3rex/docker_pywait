# docker_pywait

A wait script written in python for docker/docker-compose services:

# Usage

## Using string-check 
python pywait.py string-check --string "Service started" --url "http://whatever.service"

## Using connection
python pywait.py connection --spec tcp:some_service:3306 --spec udp:some_other_service:3306
