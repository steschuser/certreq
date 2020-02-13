#!/usr/bin/env python
import sys
import click
import getpass
import requests
from requests_ntlm import HttpNtlmAuth
import logging.handlers
from loguru import logger
from parse_it import ParseIt
from .__version__ import __title__, __version__, __configpath__
from bs4 import BeautifulSoup
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def setup_logging(verbose=False):
    # Log to syslog
    logger.remove()  # remove default logger to stdout
    handler = logging.handlers.SysLogHandler(address='/dev/log')
    if verbose:
        logger.add(sys.stderr, colorize=True, format="<level>{level}</level> | <level>{message}</level>", level="INFO")
    else:
        logger.add(sys.stderr, colorize=True, format="<level>{message}</level>", level="ERROR")
    logger.add(handler, colorize=False, format="{level} | {message}", level="INFO")


@click.group()
@click.option('-v', '--verbose/--no-verbose', default=False, help="be verbose")
@click.option('-V', '--version', default=False, help="show version")
@click.option('-c', '--config', default=__configpath__, help="config file to use", type=click.Path(exists=True))
@click.pass_context
def cli(ctx, verbose, version, config):
    parse_it = ParseIt(config_location=config)

    if version:
        print(__title__, __version__)

    setup_logging(verbose)
    ctx.ensure_object(dict)
    ctx.obj['CA'] = parse_it.read_configuration_variable("CA")
    ctx.obj['DOMAIN'] = parse_it.read_configuration_variable("DOMAIN")


@cli.command(help="list templates")
@click.option('-u', '--username', help="username")
@click.option('-p', '--password', help="prompt for password", is_flag=True)
@click.pass_context
def list(ctx, username, password):
    """list templates"""

    if password:
        password = getpass.getpass()

    session = requests.Session()
    if ctx.obj["DOMAIN"] and username:
        username = '{}\\{}'.format(ctx.obj["DOMAIN"], username)
        logger.info("username {}".format(username))

    if username and password:
        session.auth = HttpNtlmAuth(username, password)

    url = ctx.obj["CA"] + "/certsrv/certrqxt.asp"

    logger.info("accessing {}".format(url))
    r = session.get(url)

    if r.status_code == 401:
        logger.error("Unauthorized: Access is denied due to invalid credentials.")
        sys.exit(1)

    soup = BeautifulSoup(r.text, 'html.parser')
    opts = [x.text for x in soup.find(id="lbCertTemplateID").find_all("option")]
    for opt in opts:
        print(opt)


if __name__ == "__main__":
    exit(cli())
