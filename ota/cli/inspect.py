import click
import pandas as pd
import sys

from rich import inspect as rich_inspect

from ota.core.settings import get_settings
from ota.core.rpc import OdooRpc
from ota.core.console import console, COLUMNS
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
        sys.exit(1)

    console.log(f"Odoo Version: {database.odoo_version}")

    with console.status("Working..."):
        params = database.get_parameters()
        meta = database.get_meta()
        apps, apps_count = database.get_applications()
        modules, modules_count = database.get_modules()

        applications = list(
            set(apps["name"]).intersection(
                set(list(settings.models_by_applications.keys()))
            )
        )

        models = [
            v for k, v in settings.models_by_applications.items() if k in applications
        ]
        data = {}

    for k, v in params:
        console.log(f"{k}: {v}")

    console.print(
        dataframe_to_table(
            meta,
            "Metadata",
            ["name", "count"],
            column_options=dict(name=COLUMNS.name, count=COLUMNS.primary_integer),
        )
    )

    console.print(
        dataframe_to_table(
            apps,
            f"Applications ({apps_count})",
            ["name", "shortdesc"],
            column_options={
                "name": {"style": "magenta", "no_wrap": True},
                "shortdesc": {"justify": "left", "style": "green"},
            },
        )
    )

    console.print(
        dataframe_to_table(
            modules,
            f"Modules ({modules_count})",
            ["name", "shortdesc", "author"],
            column_options={
                "author": {"justify": "right", "style": "cyan", "no_wrap": True},
                "name": {"style": "magenta", "no_wrap": True},
                "shortdesc": {"justify": "center", "style": "green"},
            },
        )
    )

    for model in models:
        stats = database.get_stats(model)
        console.print(f"Model {model}: {stats['total']} record(s)")

        data[model] = {
            k: v
            for k, v in stats.items()
            if k in ["total", "this_month", "this_week", "yesterday"]
        }

        df = stats.get("top_creators")
        if not isinstance(df, pd.DataFrame) or df.empty:
            continue

        df.rename(columns={"create_uid": "name"}, inplace=True)

        console.print(
            dataframe_to_table(
                df,
                "Creators",
                ["name", "count"],
            )
        )

    df = pd.DataFrame(data)
    df = df.transpose()
    df.reset_index(inplace=True)
    df.rename(columns={"index": "name"}, inplace=True)
    total = df["total"].sum()

    col = {"justify": "center", "style": "green"}

    console.print(
        dataframe_to_table(
            df,
            f"Records ({total})",
            ["name", "yesterday", "this_week", "this_month", "total"],
            column_options={
                "name": {"style": "magenta", "no_wrap": True},
                "yesterday": col,
                "this_week": col,
                "this_month": col,
                "total": col,
            },
        )
    )
