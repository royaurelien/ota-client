from collections import namedtuple

from pydantic import BaseModel
from typing import Tuple
import pandas as pd

Columns = namedtuple(
    "Columns", ["name", "integer", "primary_integer", "text_right", "text_center"]
)

Options = namedtuple("Options", ["url", "auth_enable", "auth_method"])

File = namedtuple(
    "File",
    ["name", "path", "content"],
)


class Analysis(BaseModel):
    name: str
    modules: str
    exclude: str
    count_modules: int
    path: str

    data: dict

    res_cloc: dict
    res_odoo: dict
    res_linter: dict

    meta_exec_time: float
    meta_create_date: str

    meta_linter_version: str = ""
    meta_odoo_version: str = ""
    meta_cloc_version: str = ""

    client_version: str


class LinesOfCode(BaseModel):
    version: str
    exec_time: float
    languages: list
    data: dict

    def get_dataframe(self):
        return pd.DataFrame(self.data)
