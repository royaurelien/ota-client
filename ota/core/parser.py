# -*- coding: utf-8 -*-
#!/bin/python3

import os
import logging
import shutil
from io import StringIO
import sys
import json


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

        for k, v in odoo.modules.items():
            if modules and v.name not in modules:
                continue
            self.modules[k] = v

        self._odoo = odoo

        return self

    def analyze(self):
        output = StringIO()

        # Capture stdout to buffer
        sys.stdout = output
        self._odoo.analyse("-")
        sys.stdout = sys.__stdout__

        data = json.loads(output.getvalue())

        return data
