import click
from tabulate import tabulate
import pandas as pd
import numpy as np


from ota.core.console import console, dataframe_to_table, COLUMNS
from ota.core.parser import Parser


@click.command()
@click.argument("path")
@click.option("--modules", "-m", required=False, type=str, help="Modules")
def stats(path, modules=None, **kwargs):
    with console.status("Working..."):
        parser = Parser.from_path(path, modules)

        # data = parser.analyze()

        data = parser._odoo.export()

    # columns = {
    #     "index": "name",
    #     # "model_count": "models",
    #     # "record_count": "records",
    # }

    df = pd.DataFrame(data).transpose()
    # df.reset_index(inplace=True)
    # df.rename(columns=columns, inplace=True)

    df["missing"] = np.where(df["missing_dependency"].isnull(), False, True)
    df["missing_dependency"] = df["missing_dependency"].apply(
        lambda row: ", ".join(row) if isinstance(row, list) else row
    )
    df["depends"] = df["depends"].apply(
        lambda row: ", ".join(sorted(row)) if isinstance(row, list) else row
    )
    df["language"] = df["language"].apply(
        lambda row: ", ".join([f"{k}: {v}" for k, v in row.items()])
    )
    df["missing_dependency"] = df["missing_dependency"].fillna("")
    df = df.replace([0], "-")

    selection = [
        "name",
        "author",
        "version",
        "models_count",
        "fields",
        # "record_count",
        "records_count",
        "views_count",
        "class_count",
        # "depends_count",
        "PY",
        "XML",
        "JS",
        # "missing",
        # "missing_dependency",
        # "language",
        # "duration",
        "depends",
    ]
    df = df[selection]
    df.sort_values("name", ascending=True, inplace=True)

    # def rename_columns(df):
    #     def transform(columns):
    #         def clean(name):
    #             name = name.replace("count", "")
    #             name = name.replace("_", " ")
    #             name = name.strip()
    #             name = name.capitalize()

    #             return name

    #         new_columns = map(clean, columns)
    #         return dict(zip(columns, new_columns))

    #     return df.rename(columns=transform(list(df.columns)))

    # df = rename_columns(df)
    count = 0
    # results = df.to_dict(orient="list")

    # print(tabulate(results, headers="keys"))

    options = {
        "name": COLUMNS.name,
        "models_count": COLUMNS.integer,
        "fields": COLUMNS.integer,
        "records_count": COLUMNS.integer,
        "views_count": COLUMNS.integer,
        "class_count": COLUMNS.integer,
        "PY": COLUMNS.integer,
        "XML": COLUMNS.integer,
        "JS": COLUMNS.integer,
    }

    df = df.astype(str)

    console.print(
        dataframe_to_table(
            df,
            f"Modules ({count})",
            selection,
            column_options=options,
        )
    )
