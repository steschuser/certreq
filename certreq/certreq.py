#!/usr/bin/env python
import sys
import logging.handlers
from loguru import logger
import argparse
from .__version__ import __description__, __title__, __version__


def setup_logging(verbose=False):
    # Log to syslog
    logger.remove()  # remove default logger to stdout
    handler = logging.handlers.SysLogHandler(address='/dev/log')
    if verbose:
        logger.add(sys.stderr, colorize=True, format="<level>{level}</level> | {} | <level>{message}</level>".format(__title__), level="INFO")
    logger.add(handler, colorize=False, format="{level} | ssh-ldap | {message}", level="INFO")


def main():
    parser = argparse.ArgumentParser(description=__description__)
    subparser = parser.add_subparsers()
    parser_list = subparser.add_parser('list', help='list templates')
    parser_submit = subparser.add_parser('submit', help='submit csr')
    parser.add_argument('-v', '--verbose', help='be verbose', action='store_true')
    parser.add_argument('-V', '--version', help='show version', action='store_true')
    args = parser.parse_args()

    if args.version:
        print(__title__, __version__)
        sys.exit(0)

    setup_logging(args.verbose)


if __name__ == "__main__":
    exit(main())
