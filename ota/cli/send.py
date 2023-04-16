#!/bin/python3

import click


from ota.core.settings import get_settings
from ota.core.analyze import Analyze
from ota.core.tools import download_file, urljoin, dataframe_to_table

from ota.core.console import console


settings = get_settings()


@click.group()
def cli():
    """Odoo Technical Analysis"""


@click.command()
@click.argument("path")
@click.argument("name")
@click.option("--save", "-s", is_flag=True, default=False, type=bool, help="Save")
@click.option("--output", "-o", default="report.json", help="Create blank project")
@click.option("--exclude", "-e", default=None, type=str, help="Exclude")
def analyze(path, name, save, exclude, output):
    """Analyze modules on path"""

    options = {}

    if exclude and isinstance(exclude, str):
        exclude = list(map(str.strip, exclude.split(",")))
        options["exclude"] = exclude

    analysis = Analyze(path=path, name=name, **options)
    analysis.run()

    if save and output:
        analysis.save(output)


@click.command()
@click.argument("file")
@click.option(
    "--local", "-l", is_flag=True, default=False, type=bool, help="Send to local server"
)
def send(file, **kwargs):
    """Send report"""
    local_send = kwargs.get("local", False)

    analysis = Analyze()
    analysis.load(file)

    base_url = settings.url if not local_send else settings.local_url
    url = urljoin(base_url, "/v1/analyze")
    analysis.send(url)
