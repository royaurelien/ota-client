#!/bin/python3

import click


from ota.core.settings import get_settings
from ota.core.analyze import Analyze
from ota.core.tools import str_to_list, get_folder_name

from ota.core.console import console


settings = get_settings()


@click.command()
@click.argument("path")
@click.option("--name", "-n", default=None, type=str, help="Report name")
@click.option("--save", "-s", is_flag=True, default=False, type=bool, help="Save")
@click.option("--output", "-o", default="report.json", help="Create blank project")
@click.option("--exclude", "-e", default=None, type=str, help="Exclude")
@click.option("--modules", "-m", default=None, type=str, help="Modules")
def analyze(path, name, save, exclude, modules, output):
    """Analyze modules on path"""

    modules = str_to_list(modules)
    exclude = str_to_list(exclude)

    if not name:
        name = get_folder_name(path)

    analysis = Analyze(
        path=path,
        name=name,
        modules=modules,
        exclude=exclude,
    )
    analysis.scan_path()

    if not analysis.has_modules:
        console.log("Path does not contain any Odoo modules.")
        exit(1)

    console.log(f"{analysis.modules_count} module(s) found.")

    analysis.count_lines_of_code()
    console.print(analysis.stats.get_dataframe())

    # options = {}

    # if exclude and isinstance(exclude, str):
    #     exclude = list(map(str.strip, exclude.split(",")))
    #     options["exclude"] = exclude

    # analysis = Analyze(path=path, name=name, **options)
    # analysis.run()

    # if save and output:
    #     analysis.save(output)
