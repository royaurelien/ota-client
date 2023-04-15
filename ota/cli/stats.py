import click


from ota.core.console import console, COLUMNS
from ota.core.tools import dataframe_to_table
from ota.core.parser import Parser


@click.command()
@click.argument("path")
@click.option("--modules", "-m", required=False, type=str, help="Modules")
def stats(path, modules=None, **kwargs):
    with console.status("Working..."):
        parser = Parser.from_path(path, modules)
        df = parser.analyze()

    count = 0
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
    df = df.astype(str)

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

    console.print(
        dataframe_to_table(
            df,
            f"Modules ({count})",
            selection,
            column_options=options,
        )
    )
