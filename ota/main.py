#!/bin/python3

import click

from ota.core.settings import get_settings

settings = get_settings()  # pylint: disable=C0413

# from ota.core.console import console, dataframe_to_table
from ota.cli.inspect import inspect
from ota.cli.config import config
from ota.cli.analyze import analyze
from ota.cli.send import send
from ota.cli.download import download


@click.group()
def cli():
    """Odoo Technical Analysis"""


cli.add_command(analyze)
cli.add_command(inspect)
cli.add_command(send)
cli.add_command(download)
cli.add_command(config)
