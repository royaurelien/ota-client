import click


from ota.core.settings import get_settings
from ota.core.tools import download_file, urljoin

# from ota.core.console import console


settings = get_settings()


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
    base_url = settings.url if not local_download else settings.local_url
    url = urljoin(base_url, settings.api_report_url + f"/{id}")

    params = dict(ttype=format)
    template = kwargs.get("template")
    if template:
        params["template"] = template

    download_file(url, params)
