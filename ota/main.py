# -*- coding: utf-8 -*-
#!/bin/python3

import click

from ota.core.analyze import Analyze
from ota.core.net import download_file, urljoin


@click.group()
def cli():

    """Odoo Technical Analysis"""


@click.command()
@click.argument("path")
@click.argument("name")
@click.option("--save", "-s", is_flag=True, default=False, type=bool, help="Save")
@click.option("--output", "-o", default="report.json", help="Create blank project")
def analyze(path, name, save, output):

    analysis = Analyze(path=path, name=name)
    analysis.run()

    if save and output:
        analysis.save(output)


@click.command()
@click.argument("file")
@click.option(
    "--local", "-l", is_flag=True, default=False, type=bool, help="Send to local server"
)
def send(file, **kwargs):
    local_send = kwargs.get("local", False)

    analysis = Analyze()
    analysis.load(file)

    if local_send:
        analysis.send("http://0.0.0.0:80/v1/analyze")
        # analysis.send("http://127.0.0.1:8000/v1/analyze")


@click.command()
@click.argument("id")
@click.argument("format")
@click.option(
    "--local",
    "-l",
    is_flag=True,
    default=False,
    type=bool,
    help="Download from local server",
)
def download(id, format, **kwargs):
    local_download = kwargs.get("local", False)
    if local_download:
        base_url = "http://0.0.0.0:80/v1/report/"

    url = urljoin(base_url, id)
    download_file(url, dict(ttype=format))


cli.add_command(analyze)
cli.add_command(send)
cli.add_command(download)
