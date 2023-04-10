# -*- coding: utf-8 -*-
#!/bin/python3

import click

from ota.core.config import Config
from ota.core.analyze import Analyze
from ota.core.net import download_file, urljoin

LOCAL_URL = "http://0.0.0.0:8080"

settings = Config()


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

    base_url = settings.options.url if not local_send else LOCAL_URL
    url = urljoin(base_url, "/v1/analyze")
    analysis.send(url)


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
@click.option(
    "--template",
    "-t",
    default=False,
    type=str,
    help="Template",
)
def download(id, format, **kwargs):
    """Download report"""

    local_download = kwargs.get("local", False)
    base_url = settings.options.url if not local_download else LOCAL_URL
    url = urljoin(base_url, f"/v1/report/{id}")

    params = dict(ttype=format)
    template = kwargs.get("template")
    if template:
        params["template"] = template

    download_file(url, params)


@click.command()
@click.argument("name")
@click.argument("value")
def set(name, value, **kwargs):
    settings.set_value(name, value)


@click.command()
def get(**kwargs):
    for k, v in settings.options._asdict().items():
        print(f"{k}: {v}".format(k, v))


@click.group()
def config():
    """Configuration"""


config.add_command(set)
config.add_command(get)

cli.add_command(analyze)
cli.add_command(send)
cli.add_command(download)
cli.add_command(config)
