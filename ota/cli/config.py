#!/bin/python3

import click


from ota.core.config import Config
from ota.core.console import console, dataframe_to_table


settings = Config()


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
    try:
        value = getattr(settings.options, name)
    except AttributeError:
        value = f"Unknown variable '{name}'"
    console.print(value)


@click.command()
def view(**kwargs):
    """View"""
    # for k, v in settings.options._asdict().items():
    #     print(f"{k}: {v}".format(k, v))

    console.print(settings.options._asdict())


@click.group()
def config():
    """Manage configuration"""


config.add_command(set_value)
config.add_command(get_value)
config.add_command(view)
