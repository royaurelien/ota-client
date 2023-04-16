import click

from ota.core.console import console, Panel, COLUMNS
from ota.core.tools import dataframe_to_table
from ota.core.parser import Parser


@click.command()
@click.argument("path")
@click.option("--modules", "-m", required=False, type=str, help="Modules")
def stats(path, modules=None, **kwargs):
    with console.status("Working..."):
        parser = Parser.from_path(path, modules)
        df, linter = parser.analyze()

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
        # "code",
        "comment",
        "docstring",
        # "empty",
        # "total",
        # "missing",
        # "missing_dependency",
        # "language",
        # "duration",
        "score",
        "depends",
    ]
    df = df[selection]

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
        "score": COLUMNS.primary_integer,
    }

    console.print(
        dataframe_to_table(
            df,
            f"Modules ({len(df)})",
            selection,
            column_options=options,
        )
    )

    # Only one module, show linter messages
    if len(linter.keys()) == 1:
        linter = linter[next(iter(linter))]
        df = linter["messages"]

        selection = ["module", "line", "column", "category", "msg_id", "symbol", "msg"]

        duplicate_code = df[(df["symbol"] == "duplicate-code")]

        df.drop(duplicate_code.index, inplace=True)
        df.sort_values(["module", "line"], ascending=True, inplace=True)

        options = {
            "module": COLUMNS.name,
            "column": COLUMNS.integer,
            "line": COLUMNS.primary_integer,
            "msg": COLUMNS.text_right,
            "category": COLUMNS.text_center,
            "msg_id": COLUMNS.text_center,
            "symbol": COLUMNS.text_center,
        }

        console.print(
            dataframe_to_table(
                df,
                f"Messages ({len(df)})",
                selection,
                column_options=options,
            )
        )

        if not duplicate_code.empty:
            console.print(
                Panel.fit(
                    f"Duplicates code ({len(duplicate_code)})", border_style="red"
                )
            )
            for code in duplicate_code["msg"].values:
                console.print(code)
