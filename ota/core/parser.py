#!/usr/bin/env python3

import logging

import pandas as pd
import numpy as np

from ota.odoo import Odoo

MANIFESTS = ["__manifest__.py", "__odoo__.py", "__openerp__.py"]


_logger = logging.getLogger(__name__)


class Parser(object):
    def __init__(self, path):
        self.path = path
        self.modules = {}

        self._odoo = None

    @classmethod
    def from_path(cls, path, modules=None):
        self = cls(path)

        if modules and not isinstance(modules, list):
            modules = list(set(map(str.strip, modules.split(","))))

        odoo = Odoo.from_path(path)

        # Apply the filter
        if modules:
            odoo.modules = {
                name: module for name, module in odoo.items() if name in modules
            }

        for k, v in odoo.modules.items():
            if modules and v.name not in modules:
                continue
            self.modules[k] = v

        self._odoo = odoo

        return self

    def analyze(self):
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
