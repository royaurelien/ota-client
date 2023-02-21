# -*- coding: utf-8 -*-
#!/bin/python3

import json

message = """
Please install the cloc package first.
Refer to https://github.com/AlDanial/cloc#install-via-package-manager
"""

try:
    from sh import cloc
except ImportError as error:
    print(message)
    exit(1)


def run_cloc(path):
    res = cloc([path, "--json"])
    data = json.loads(res.stdout)

    return data
