import click


from ota.core.settings import get_settings
from ota.core.analyze import Analyze
from ota.core.tools import str_to_list, get_folder_name, dataframe_to_table

from ota.core.console import console, Panel, COLUMNS


settings = get_settings()


@click.command()
@click.argument("path")
@click.option("--name", "-n", default=None, type=str, help="Report name")
@click.option("--save", "-s", is_flag=True, default=False, type=bool, help="Save")
@click.option("--output", "-o", default="report.json", help="Create blank project")
@click.option("--verbose", "-v", default=True, type=bool, help="Verbose")
@click.option("--exclude", "-e", default=None, type=str, help="Exclude")
@click.option("--modules", "-m", default=None, type=str, help="Modules")
def analyze(path, name, save, verbose, exclude, modules, output):
    """Analyze modules on path"""

    to_keep = str_to_list(modules)
    to_exclude = str_to_list(exclude)

    if not name:
        name = get_folder_name(path)

    with console.status("Working..."):
        analysis = Analyze(
            name,
            path=path,
            to_keep=to_keep,
            to_exclude=to_exclude,
        )
        analysis.scan_path()

        if not analysis.has_modules:
            console.log("Path does not contain any Odoo modules.")
            exit(1)

        analysis.run()

        if not analysis.is_ok:
            console.log("Modules are not equals.")
            exit(1)

        analysis.export()

    if save:
        analysis.save(output)
        console.log(f"Analysis saved to {output}")

    if verbose:
        console.log(f"Analyze '{name}'")
        console.log(f"{analysis.modules_count} module(s) found.\n")

        df = analysis.stats.get_dataframe()

        console.log(f"{analysis.stats.languages_count} languages:")
        for item in analysis.stats.get_summary():
            console.log("\t" + item)

        df = analysis.get_dataframe()

        selection = [
            "name",
            "author",
            "version",
            "models_count",
            "fields",
            "records_count",
            "views_count",
            "class_count",
            "PY",
            "XML",
            "JS",
            # "comment",
            # "docstring",
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
        if analysis.modules_count == 1:
            linter = analysis.linter_by_modules[0]
            df = linter.get_dataframe()

            if not df.empty:
                options = {
                    "file": COLUMNS.name,
                    "line": COLUMNS.primary_integer,
                    "column": COLUMNS.integer,
                    # "module": COLUMNS.name,
                    "msg_id": COLUMNS.text_center,
                    "category": COLUMNS.text_center,
                    "symbol": COLUMNS.text_center,
                    "msg": COLUMNS.text_right,
                }

                console.print(
                    dataframe_to_table(
                        df,
                        f"Messages ({len(df)})",
                        list(options.keys()),
                        column_options=options,
                    )
                )

            if linter.has_duplicates:
                console.print(
                    Panel.fit(
                        f"Duplicates code ({linter.duplicates_count})",
                        border_style="red",
                    )
                )
                for code in linter.duplicates:
                    console.print(code)
