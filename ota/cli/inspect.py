import click
import pandas as pd

from ota.core.settings import get_settings
from ota.core.rpc import OdooRpc
from ota.core.console import console
from ota.core.tools import dataframe_to_table

settings = get_settings()


@click.command()
@click.argument("database")
@click.option("--host", "-h", default=None, type=str, help="Odoo Host")
@click.option("--user", "-u", default=None, type=str, help="User")
@click.option("--password", "-p", default=None, type=str, help="Password")
@click.option(
    "--local",
    "-l",
    is_flag=True,
    default=False,
    type=bool,
    help="Use local database with default credentials",
)
def inspect(database, host, user, password, local):
    """Inspect Database"""

    if local:
        host, user, password = settings.get_local_credentials()

    database = OdooRpc(host, database, user, password)

    if not database.is_connected:
        console.log(f"Connection to {database} database failed.")
        exit(1)

    with console.status("Working..."):
        apps, count = database.get_applications()

        options = {
            "name": {"style": "magenta", "no_wrap": True},
            "shortdesc": {"justify": "left", "style": "green"},
        }

        console.print(
            dataframe_to_table(
                apps,
                f"Applications ({count})",
                ["name", "shortdesc"],
                column_options=options,
            )
        )

        modules, count = database.get_modules()

        options = {
            "author": {"justify": "right", "style": "cyan", "no_wrap": True},
            "name": {"style": "magenta", "no_wrap": True},
            "shortdesc": {"justify": "center", "style": "green"},
        }

        console.print(
            dataframe_to_table(
                modules,
                f"Modules ({count})",
                ["name", "shortdesc", "author"],
                column_options=options,
            )
        )

    applications = list(
        set(modules["name"]).intersection(
            set(list(settings.models_by_applications.keys()))
        )
    )
    models = [
        v for k, v in settings.models_by_applications.items() if k in applications
    ]
    data = {}

    for model in models:
        stats = database.get_stats(model)
        console.print(f"Model {model}: {stats['total']} record(s)")

        data[model] = {
            k: v
            for k, v in stats.items()
            if k in ["total", "this_month", "this_week", "yesterday"]
        }

        # console.print(tabulate(stats["by_day"], headers="keys"))

        df = stats["top_creators"]
        df = df.astype(str)
        df.rename(columns={"create_uid": "name"}, inplace=True)

        console.print(
            dataframe_to_table(
                df,
                "Creators",
                ["name", "count"],
                # column_options=options,
            )
        )

    df = pd.DataFrame(data)
    df = df.transpose()
    df.reset_index(inplace=True)
    df.rename(columns={"index": "name"}, inplace=True)
    df = df.astype(str)

    col = {"justify": "center", "style": "green"}
    options = {
        "name": {"style": "magenta", "no_wrap": True},
        "yesterday": col,
        "this_week": col,
        "this_month": col,
        "total": col,
    }

    console.print(
        dataframe_to_table(
            df,
            "Records",
            ["name", "yesterday", "this_week", "this_month", "total"],
            column_options=options,
        )
    )
