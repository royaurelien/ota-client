#!/bin/python3

from io import StringIO
import json
import sys

from odoo_analyse import Odoo


def to_json_patched(self):
    data = {
        "path": self.path,
        "name": self.name,
        "duration": self.duration,
        "manifest": self.manifest,
        "models": {n: m.to_json() for n, m in self.models.items()},
        "classes": {n: c.to_json() for n, c in self.classes.items()},
        "views": {n: v.to_json() for n, v in self.views.items()},
        "records": {n: d.to_json() for n, d in self.records.items()},
        "depends": list(self.depends),
        "imports": list(self.imports),
        "refers": list(self.refers),
        "files": list(self.files),
        "status": list(self.status),
        "language": self.language,
        "words": list(self.words),
        "hashsum": self.hashsum,
        "readme": bool(self.readme),
        "readme_type": self.readme_type,
        "author": self.author,
        "category": self.category,
        "license": self.license,
        "version": self.version,
        "info": self.info,
    }
    if self.manifest and "data" in self.manifest:
        data["manifest"]["data"] = list(data["manifest"]["data"])

    return data


def run_odoo_analyse(path, exclude=[]):
    odoo = Odoo.from_path(path)

    output = StringIO()

    # Capture stdout to buffer
    sys.stdout = output
    odoo.analyse("-")
    sys.stdout = sys.__stdout__

    data = json.loads(output.getvalue())

    # data = {k: to_json_patched(m) for k, m in odoo.full.items()}

    for name in data.keys():
        vals = to_json_patched(odoo.modules[name])
        data[name].update(vals)

    modules = sorted([name for name, obj in odoo.items() if name not in exclude])

    return modules, data
