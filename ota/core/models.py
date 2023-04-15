from collections import namedtuple

from pydantic import BaseModel
from typing import Tuple

Columns = namedtuple("Columns", ["name", "integer"])

Options = namedtuple("Options", ["url", "auth_enable", "auth_method"])


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
