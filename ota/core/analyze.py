import json
import os
import pkgutil
import time

import pandas as pd
import numpy as np

# pylint: disable=C0413
CLOC_WARNING = """
Please install the cloc package first.
Refer to https://github.com/AlDanial/cloc#install-via-package-manager
"""

try:
    from sh import cloc
except ImportError as error:
    print(CLOC_WARNING)
    exit(1)


from ota.core.tools import (
    now,
    save_to_json,
    save_to,
    to_json,
    load_from_json,
    run_pylint,
    PYLINT_VERSION,
)
from ota.core.models import LinesOfCode, LocalModule, LinterResult
from ota.odoo import Odoo, ODOO_VERSION


class Analyze(object):
    __version__ = "0.1.0"

    path: str
    name: str
    to_exclude: list = []
    to_keep: list = []
    _modules: list = []
    _odoo = None
    _database = None
    modules: str = []
    linter_by_modules: list = []
    linter = None
    stats = None

    meta_odoo_version: str = False
    meta_cloc_version: str = False
    meta_linter_version: str = False
    meta_create_date: str = False
    meta_exec_time: float = False

    def __init__(self, name, **kwargs):
        self.name = name
        self.__dict__.update(kwargs)

    def scan_path(self):
        """Search for Odoo modules at path"""
        modules = list(pkgutil.walk_packages([self.path]))

        # Is path a package?
        res = [
            os.path.basename(item.module_finder.path)
            for item in filter(lambda item: item.name == "__manifest__", modules)
        ]

        if not res:
            res = [item.name for item in filter(lambda item: item.ispkg, modules)]

        # FIXME: filter modules
        res = set(res)

        if self.to_keep:
            res = res.intersection(set(self.to_keep))
        if self.to_exclude:
            res = res.difference(set(self.to_exclude))

        self._modules = list(res)

    @property
    def has_modules(self):
        return bool(self._modules)

    @property
    def modules_count(self):
        return len(self._modules) if self._modules else len(self.modules)

    def count_lines_of_code(self):
        """Cout lines of code"""
        self.stats = self._count_lines_of_code(self.path)

    def _count_lines_of_code(self, path):
        start = time.perf_counter()

        res = cloc([path, "--json"])
        data = json.loads(res.stdout)

        header = data.pop("header")
        cloc_version = header.get("cloc_version", "0.0")
        df = pd.DataFrame(data)
        df = df.loc[:, df.columns != "SUM"]
        df.rename(columns={k: k.lower().capitalize() for k in df.columns}, inplace=True)

        languages = list(df.columns)
        df = df.transpose()

        files = df["nFiles"].to_dict()
        df = df.loc[:, df.columns != "nFiles"]
        df["total"] = df["blank"] + df["comment"] + df["code"]

        lines = df["code"].to_dict()
        # df = df.transpose()

        obj = LinesOfCode(
            version=cloc_version,
            exec_time=(time.perf_counter() - start),
            languages=languages,
            lines=lines,
            files=files,
            data=df.to_dict(),
        )

        return obj

    def load_modules(self):
        """Load modules from odoo_analyse"""
        odoo = Odoo.from_path(self.path)

        if self.to_keep:
            odoo.modules = {
                name: module for name, module in odoo.items() if name in self.to_keep
            }
        elif self.to_exclude:
            odoo.modules = {
                name: module
                for name, module in odoo.items()
                if name not in self.to_exclude
            }

        self._odoo = odoo
        self.modules = self._odoo.export()

    @property
    def is_ok(self):
        return set(k for k, v in self._odoo.items()) == set(self._modules)

    def get_dataframe(self):
        data = {mod.name: vars(mod) for mod in self.modules}
        df = pd.DataFrame(data).transpose()

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
        df["score"] = df["score"].apply(lambda row: "PERFECT" if row == 10.0 else row)
        df["missing_dependency"] = df["missing_dependency"].fillna("")
        df = df.replace([0], "-")

        df.sort_values("name", ascending=True, inplace=True)

        return df

    def run_linter(self):
        """Run linter"""
        # Run once globally
        self.linter = run_pylint(self.path, recursive=True)

        if self.modules_count:
            for mod in self.modules:
                res = run_pylint(mod.path, name=mod.name)

                # Set score on module
                mod.score = res.score
                self.linter_by_modules.append(res)

    def export(self):
        vals = {
            "name": self.name,
            "args": {
                "modules_to_keep": self.to_keep,
                "modules_to_exclude": self.to_exclude,
            },
            "modules_count": self.modules_count,
            "path": self.path,
            "stats": vars(self.stats),
            "modules": {mod.name: vars(mod) for mod in self.modules},
            "linter_by_modules": {
                mod.name: vars(mod) for mod in self.linter_by_modules
            },
            "linter": self.linter.get_summary(),
            "meta_exec_time": self.meta_exec_time,
            "meta_create_date": self.meta_create_date or now(),
            "meta_linter_version": self.meta_linter_version or PYLINT_VERSION,
            "meta_odoo_version": self.meta_odoo_version or ODOO_VERSION,
            "meta_cloc_version": self.meta_cloc_version or self.stats.version,
            "meta_ota_version": self.__version__,
        }

        # FIXME: jsonify
        # vals["modules"].update({mod.name: vars(mod) for mod in self.linter_by_modules})
        data = to_json(vals)
        # data["linter"] = self.linter.json()

        return data

    def run(self, **kwargs):
        start = time.perf_counter()

        self.count_lines_of_code()
        self.load_modules()
        self.run_linter()

        self.meta_exec_time = time.perf_counter() - start

    def save(self, filepath):
        save_to(self.export(), filepath)

    @classmethod
    def load(cls, filepath):
        data = load_from_json(filepath)

        version = data.get("meta_ota_version", False)

        if cls.__version__ != version:
            raise NotImplementedError(
                f"Load data from {version} version is not supported."
            )

        self = cls(data["name"])

        attrs = [
            "path",
            "meta_exec_time",
            "meta_create_date",
            "meta_linter_version",
            "meta_odoo_version",
            "meta_cloc_version",
        ]

        self.__dict__.update({k: v for k, v in data.items() if k in attrs})
        self.__dict__.update(
            {
                "to_keep": data.get("args", {}).get("modules_to_keep", []),
                "to_exclude": data.get("args", {}).get("modules_to_exclude", []),
            }
        )

        self.modules = [LocalModule(**vals) for vals in data["modules"].values()]
        self.stats = LinesOfCode(**data["stats"])
        self.linter = LinterResult(**{"name": "global", **data["linter"]})
        self.linter_by_modules = [
            LinterResult(**vals) for name, vals in data["linter_by_modules"].items()
        ]

        return self
