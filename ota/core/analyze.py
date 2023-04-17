# -*- coding: utf-8 -*-
#!/bin/python3


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


# from ota.tools.odoo import run_odoo_analyse
# from ota.tools.pylint import run_pylint, pylint_version
from ota.core.tools import (
    send_analysis,
    now,
    save_to_json,
    save_to,
    to_json,
    load_from_json,
    run_pylint,
    PYLINT_VERSION,
)
from ota.core.models import LinesOfCode
from ota.odoo import Odoo
from ota.core.console import console


class Analyze(object):
    __version__ = "0.1.0"

    modules: list = []
    linter_by_modules: list = []
    linter = None
    stats = None

    exec_time = 0.0

    def __init__(self, **kwargs):
        self.path = ""
        self.name = ""
        self.to_exclude = []
        self.to_keep = []

        self._modules = []
        self._odoo = None
        self._database = None

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
        return len(self._modules)

    def count_lines_of_code(self):
        """Cout lines of code"""
        self.stats = self._count_lines_of_code(self.path)

    def _count_lines_of_code(self, path):
        start = time.perf_counter()

        res = cloc([path, "--json"])
        data = json.loads(res.stdout)

        header = data.pop("header")
        cloc_version = header.get("cloc_version", "0.0")
        languages = list(filter(lambda item: item != "SUM", data.keys()))

        obj = LinesOfCode(
            version=cloc_version,
            exec_time=(time.perf_counter() - start),
            languages=languages,
            data=data,
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

        if self.modules_count > 1:
            for mod in self.modules:
                res = run_pylint(mod.path, name=mod.name)

                # Set score on module
                mod.score = res.score
                self.linter_by_modules.append(res)
        elif self.modules_count == 1:
            self.modules[0].score = self.linter.score
            self.linter_by_modules = [self.linter]

    def export(self):
        vals = {
            "name": self.name,
            "args": {
                "modules_to_keep": self.to_keep,
                "modules_to_exclude": self.to_exclude,
            },
            "count_modules": self.modules_count,
            "path": self.path,
            "stats": self.stats.data,
            "languages": self.stats.languages,
            "modules": {mod.name: vars(mod) for mod in self.modules},
            "linter_by_modules": {
                mod.name: vars(mod) for mod in self.linter_by_modules
            },
            "linter": self.linter.get_summary(),
            "meta_exec_time": self.exec_time,
            "meta_create_date": now(),
            "meta_linter_version": PYLINT_VERSION,
            "meta_odoo_version": self._odoo.version,
            "meta_cloc_version": self.stats.version,
            "meta_ota_version": self.__version__,
        }
        # vals["modules"].update({mod.name: vars(mod) for mod in self.linter_by_modules})
        data = to_json(vals)
        # data["linter"] = self.linter.json()

        return data

    def run(self, **kwargs):
        start = time.perf_counter()

        self.count_lines_of_code()
        self.load_modules()
        self.run_linter()

        self.exec_time = time.perf_counter() - start

        # # Prepare values to export
        # self.data = {
        #     "name": self.name,
        #     "modules": modules,
        #     "exclude": self.exclude,
        #     "count_modules": len(modules),
        #     "path": self.path,
        #     "data": {
        #         "analyze_cloc": cloc_data,
        #         "analyze_odoo": odoo_analyse_data,
        #         "analyze_pylint": pylint_data,
        #     },
        #     "execution_time": end - start,
        #     "create_date": datetime.now().strftime("%Y%m%d %H:%M:%S"),
        #     "pylint_version": pylint_version,
        #     # 'odoo_analyse_version': Odoo.__version__,
        # }

    def save(self, filepath):
        save_to(self.export(), filepath)

    def load(self, filepath):
        data = load_from_json(filepath)

        self.data = data
        self.path = data.get("path")
        self.name = data.get("name")
        self.exclude = data.get("exclude")

    def send(self, url):
        status_code, data = send_analysis(url, self.data)

        print(data.get("id"))
