import json
import sys

import click

from ota.core.console import console
from ota.core.settings import get_settings
from ota.core.tools import post_json, urljoin

settings = get_settings()


@click.command()
@click.argument("file")
@click.option(
    "--local", "-l", is_flag=True, default=True, type=bool, help="Send to local server"
)
@click.option(
    "--parseable",
    "-p",
    is_flag=True,
    default=False,
    type=bool,
    help="Make result parseable",
)
def send(file, parseable, **kwargs):
    """Send report"""
    local_send = kwargs.get("local", False)

    # analysis = Analyze.load(file)
    # data = analysis.export()

    with open(file, encoding="utf-8") as f:
        data = json.load(f)

    base_url = settings.url if not local_send else settings.local_url

    if not base_url:
        console.log("Base Url is not defined.")
        sys.exit(1)

    url = urljoin(base_url, settings.api_analyze_url)
    status, resp, msg = post_json(url, data)

    if not status:
        if not parseable:
            console.log(msg)

        sys.exit(1)

    res_id = resp.get("id")

    if not parseable:
        console.log(f"Analysis ID: {res_id}")
    else:
        print(res_id)
