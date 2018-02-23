# docker_pywait

A wait script written in python for docker/docker-compose services
Tested for now only with python 2.7 and 3.6

# Usage

## Using string-check 
python pywait.py string-check --string "Service started" --url "http://whatever.service"

## Using connection
python pywait.py connection --spec tcp:some_service:3306 --spec udp:some_other_service:3306

## Customize timeouts, retries and exit code errors
python pywait.py --retries 15 --timeout 6 --exit-code 124 connection --spec tcp:some_service:3306

## Quiet any output
python pywait.py --quiet connection --spec tcp:some_service:3306
