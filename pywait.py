#!/usr/bin/env python3

import argparse
import re
import sys
import time
import socket
from urllib.request import urlopen
from contextlib import closing

parser = argparse.ArgumentParser(description='Waits for a service to start')
subparsers = parser.add_subparsers(help='Specify which type of wait type should we try', dest="command")
subparsers.required = True
parser.add_argument('--retries', '-r', type=int, default=10, help="The number of retries")
parser.add_argument('--timeout', '-t', type=int, default=5, help="The number of seconds to delay")
parser.add_argument('--exit-code', '-e', type=int, default=4, help="The exitcode used in case of errors")
parser.add_argument('--quiet', '-q', action='store_true', help="Whether to show any output")

string_check_parser = subparsers.add_parser(
    'string-check',
    description='Checks that a string is returned at specific URL'
)

connection_check_parser = subparsers.add_parser(
    'connection',
    description='Checks that a specific port is opened'
)

# String check
group = string_check_parser.add_argument_group('String check type')
group_exclusive = group.add_mutually_exclusive_group()
group_exclusive.add_argument('--string', '-s', type=str, help='The string to check for')
group_exclusive.add_argument('--regex', '-g', type=str, help='The regex to check for')
string_check_parser.add_argument('--url', '-u', type=str, help='The URL to check against')


def log(message):
    if not args.quiet:
        print(message)


def valid_connection_spec(connection_spec):
    spec_parts = connection_spec.split(':')
    valid_protocol_specs = ['tcp', 'udp']
    if len(spec_parts) != 3:
        raise ValueError('Invalid spec. Should be (tcp|udp):<name>:<port>')

    if spec_parts[0] not in valid_protocol_specs:
        raise ValueError('Invalid spec. Protocol should any of ' + ' '.join(valid_protocol_specs))

    return tuple(spec_parts)


# Connection check
connection_check_parser.add_argument(
    "--spec", "-p", type=valid_connection_spec,
    help="A spec in the form of (tcp|udp):<name>:<port>"
)
connection_check_parser.add_argument('--timeout', '-t', default=2, type=int, help='Default socket timeout')
args = parser.parse_args()

if 'string-check' == args.command:
    for j in range(1, args.retries + 1):
        checker = args.string if args.string else args.regex
        checker = re.compile(checker, flags=re.IGNORECASE | re.MULTILINE)
        log("Starting retry number #" + str(j))

        try:
            content = urlopen(args.url).read().decode('utf-8')
            if checker.match(content):
                log('Done with success.')
                sys.exit(0)
        except Exception as ex:
            log('Failed with: ' + str(ex))
            time.sleep(args.timeout)

if 'connection' == args.command:
    for j in range(1, args.retries + 1):
        address = args.spec[1]
        port = int(args.spec[2])
        proto = socket.SOCK_DGRAM if 'udp' == args.spec[0] else socket.SOCK_STREAM

        with closing(socket.socket(socket.AF_INET, proto)) as s:
            try:
                s.settimeout(args.timeout)
                result = s.connect((address, port))
                s.shutdown(2)

                log('Done with success.')
                sys.exit(0)
            except Exception as ex:
                log('Failed to connect: ' + str(ex))
                time.sleep(args.timeout)
            finally:
                s.close()

log('Failed waiting. Exiting ...')
sys.exit(args.exit_code)