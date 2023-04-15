#!/bin/python3

import click


from ota.core.settings import get_settings
from ota.core.console import console

# from ota.core.tools import dataframe_to_table


settings = get_settings()


@click.command()
@click.argument("name")
@click.argument("value")
def set_value(name, value, **kwargs):
    """Set settings value"""
    settings.set_value(name, value)


@click.command()
@click.argument("name")
def get_value(name, **kwargs):
    """Get settings value"""
    value = settings.get_value(name)
    console.print(value)


@click.command()
def view(**kwargs):
    """View"""
    # for k, v in settings.options._asdict().items():
    #     print(f"{k}: {v}".format(k, v))

    console.print(settings)


@click.group()
def config():
    """Manage configuration"""


config.add_command(set_value)
config.add_command(get_value)
config.add_command(view)
