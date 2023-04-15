# -*- coding: utf-8 -*-
#!/bin/python3


from datetime import datetime
import json
import os
import time

from ota.tools.cloc import run_cloc
from ota.tools.odoo import run_odoo_analyse
from ota.tools.pylint import run_pylint, pylint_version

from ota.core.tools import send_analysis


class Analyze(object):
    def __init__(self, **kwargs):
        self.path = ""
        self.name = ""
        self.exclude = []
        self.data = {}

        self.__dict__.update(kwargs)

    def run(self):
        start = time.perf_counter()
        # 0. Cloc
        cloc_data = run_cloc(self.path)

        # 1. Odoo Analyse
        modules, odoo_analyse_data = run_odoo_analyse(self.path, self.exclude)

        # 2. PyLint Analyse
        pylint_data = run_pylint(self.path, modules)

        end = time.perf_counter()

        # Prepare values to export
        self.data = {
            "name": self.name,
            "modules": modules,
            "exclude": self.exclude,
            "count_modules": len(modules),
            "path": self.path,
            "data": {
                "analyze_cloc": cloc_data,
                "analyze_odoo": odoo_analyse_data,
                "analyze_pylint": pylint_data,
            },
            "execution_time": end - start,
            "create_date": datetime.now().strftime("%Y%m%d %H:%M:%S"),
            "pylint_version": pylint_version,
            # 'odoo_analyse_version': Odoo.__version__,
        }

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
