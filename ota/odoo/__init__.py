from io import StringIO
import sys
from importlib import metadata


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
from ota.core.models import LocalModule


ODOO_VERSION = metadata.version("odoo_analyse")


class Odoo(OOdoo):
    __output__ = None

    def load_path(self, paths, depth=None):
        """Overrided to replace Module"""

        if isinstance(paths, str):
            paths = [paths]

        result = Module.find_modules(paths, depth=depth)

        self.full.update(result.copy())
        self.modules.update(result.copy())

    def _analyse_out_json(self, data, file_path):
        """Output the analyse result as JSON"""

        # FIXME: overrided
        self.__output__ = data

    def export(self):
        output = StringIO()

        # Capture stdout to buffer
        sys.stdout = output
        self.analyse("-")
        sys.stdout = sys.__stdout__

        data = self.__output__
        for name in data.keys():
            vals = self.modules[name].to_json()
            data[name].update(vals)

        return [LocalModule(**values) for values in data.values()]

    # def filter_on_database(self):
    #     names = []
    #     # Apply the filter
    #     self.modules = {name: module for name, module in self.items() if name in names}
