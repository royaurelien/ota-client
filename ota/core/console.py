from collections import namedtuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ota.core.tools import humanize

console = Console()

Columns = namedtuple("Columns", ["name", "integer"])
COLUMNS = Columns(
    integer={"justify": "center", "style": "green"},
    name={"style": "magenta", "no_wrap": True},
)

# DEFAULT_OPTIONS = {
#     "name": {"style": "magenta", "no_wrap": True},
# }


def dataframe_to_table(df, title, columns, **kwargs):
    table = Table(title=title)
    df = df[columns]

    options = kwargs.get("column_options", {})

    for name, title in zip(columns, map(humanize, list(df))):
        column_options = options.get(name, {})
        table.add_column(title, **column_options)

    data = df.to_dict(orient="split")

    for line in data["data"]:
        table.add_row(*line)

    return table


# def dict_to_table(vals_list, title, columns=[], **kwargs):
#     table = Table(title=title)
#     options = kwargs.get("column_options", {})

#     if not columns:
#         columns = list(vals_list[0].keys())

#     print(columns)

#     for name, title in zip(columns, map(humanize, columns)):
#         column_options = options.get(name, {})
#         table.add_column(title, **column_options)

#     for vals in vals_list:
#         values = [str(v) for k, v in vals.items() if k in columns]
#         print(values)
#         table.add_row(*values)
