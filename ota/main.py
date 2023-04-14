#!/bin/python3

import click

from ota.core.config import Config

# from ota.core.console import console, dataframe_to_table
from ota.cli.inspect import inspect
from ota.cli.config import config
from ota.cli.analyze import analyze, send, download
from ota.cli.stats import stats

LOCAL_URL = "http://0.0.0.0:8080"

settings = Config()


@click.group()
def cli():
    """Odoo Technical Analysis"""


cli.add_command(analyze)
cli.add_command(inspect)
cli.add_command(send)
cli.add_command(download)
cli.add_command(config)
cli.add_command(stats)
