# -*- coding: utf-8 -*-
#!/bin/python3


from odoo_analyse import Odoo


# def to_json(module):
#     return {
#         "path": module.path,
#         "name": module.name,
#         "manifest": module.manifest,
#         "models": {n: m.to_json() for n, m in module.models.items()},
#         "views": {n: v.to_json() for n, v in module.views.items()},
#         "data": module.data,
#         "depends": list(module.depends),
#         "imports": list(module.imports),
#         "refers": list(module.refers),
#         "files": list(module.files),
#         "status": list(module.status),
#         "language": module.language,
#         "words": list(module.words),
#         "hashsum": module.hashsum,
#         "readme": bool(module.readme),
#         "readme_type": module.readme_type,
#     }


def to_json(self):
    return {
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
    }


def run_odoo_analyse(path, exclude=[]):
    odoo = Odoo.from_path(path)

    # data = odoo.save_json("-")
    # data = json.dumps(data)

    # Call json dumps because save_json last character return is None or null value
    # data = json.dumps({k: m.to_json() for k, m in odoo.full.items()})

    # data = {k: m.to_json() for k, m in odoo.full.items()}
    data = {k: to_json(m) for k, m in odoo.full.items()}

    modules = sorted([name for name, obj in odoo.items() if name not in exclude])

    return modules, data
