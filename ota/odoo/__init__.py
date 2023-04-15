# -*- coding: utf-8 -*-
#!/bin/python3

import logging
from io import StringIO
import json
import sys

# import odoo_analyse
from odoo_analyse import Odoo as OOdoo
from odoo_analyse import Module as OdooModule
from odoo_analyse import Model as OdooModel
from odoo_analyse.field import Field as OdooField
from odoo_analyse.utils import get_ast_source_segment

from ota.odoo.module import Module
from ota.odoo.model import Model
from ota.odoo.field import Field

from ota.core.console import console
from ota.tools.pylint import run_pylint_once

_logger = logging.getLogger(__name__)


class Odoo(OOdoo):
    def load_path(self, paths, depth=None):
        """Overrided to replace Module"""

        if isinstance(paths, str):
            paths = [paths]

        result = Module.find_modules(paths, depth=depth)

        self.full.update(result.copy())
        self.modules.update(result.copy())

    def export(self):
        output = StringIO()

        # Capture stdout to buffer
        sys.stdout = output
        self.analyse("-")
        sys.stdout = sys.__stdout__

        data = json.loads(output.getvalue())
        linter = dict()

        for name in data.keys():
            vals = self.modules[name].to_json()
            data[name].update(vals)

            x = data[name].setdefault("missing_dependency", {})
            # data[name]["missing_dependency"] = x

            linter[name] = run_pylint_once(data[name]["path"])
            data[name]["score"] = linter[name].get("score", 0)

        return data, linter

    def filter_on_database(self):
        names = []
        # Apply the filter
        self.modules = {name: module for name, module in self.items() if name in names}
