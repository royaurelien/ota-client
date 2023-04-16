# -*- coding: utf-8 -*-
#!/bin/python3


from datetime import datetime
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
from ota.core.tools import send_analysis
from ota.core.models import LinesOfCode
from ota.odoo import Odoo


class Analyze(object):
    def __init__(self, **kwargs):
        self.path = ""
        self.name = ""
        self.exclude = []
        self.modules = []
        self.data = {}

        self.stats = None

        self._modules = []
        self._odoo = None
        self._cloc = None
        self._pylint = None
        self._database = None

        self.__dict__.update(kwargs)

    def scan_path(self):
        modules = list(pkgutil.walk_packages([self.path]))

        # Is the path a package?
        res = [
            os.path.basename(item.module_finder.path)
            for item in filter(lambda item: item.name == "__manifest__", modules)
        ]

        if not res:
            res = [item.name for item in filter(lambda item: item.ispkg, modules)]

        self._modules = list(set(res))

    @property
    def has_modules(self):
        return bool(self._modules)

    @property
    def modules_count(self):
        return len(self._modules)

    def count_lines_of_code(self):
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

    def run_odoo_analyse(self):
        odoo = Odoo.from_path(self.path)

        if self.modules:
            odoo.modules = {
                name: module for name, module in odoo.items() if name in self.modules
            }
        elif self.exclude:
            odoo.modules = {
                name: module
                for name, module in odoo.items()
                if name not in self.exclude
            }
        self._odoo = odoo

        data, linter = self._odoo.export()

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
        df["missing_dependency"] = df["missing_dependency"].fillna("")
        df = df.replace([0], "-")

        df.sort_values("name", ascending=True, inplace=True)

        return df, linter

    def run(self):
        pass
        # start = time.perf_counter()
        # # 0. Cloc
        # cloc_data = run_cloc(self.path)

        # # 1. Odoo Analyse
        # modules, odoo_analyse_data = run_odoo_analyse(self.path, self.exclude)

        # # 2. PyLint Analyse
        # pylint_data = run_pylint(self.path, modules)

        # end = time.perf_counter()

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

    def to_json(self):
        return json.dumps(self.data, indent=4)

    def save(self, filepath):
        json_object = self.to_json()

        filepath = os.path.join(filepath)
        with open(filepath, "w") as outfile:
            outfile.write(json_object)

    def load(self, filepath):
        with open(filepath, "r") as file:
            data = json.loads(file.read())

        self.data = data
        self.path = data.get("path")
        self.name = data.get("name")
        self.exclude = data.get("exclude")

    def send(self, url):
        status_code, data = send_analysis(url, self.data)

        print(data.get("id"))
