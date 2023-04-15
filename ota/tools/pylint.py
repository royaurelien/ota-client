# -*- coding: utf-8 -*-
#!/bin/python3

import logging
import os
from io import StringIO
import sys

from pylint import __version__ as pylint_version
from pylint.lint import Run
from pylint.reporters.text import TextReporter
from pylint.reporters import JSONReporter
import pandas as pd

from ota.core.console import console

logging.basicConfig(filename="error.log", level=logging.DEBUG)


def round_float(value, digits=2):
    return round(value, digits)


def _prepare_stats(stats):
    return {
        # 'success': bool(stats.global_note >= threshold),
        "score": round_float(stats.global_note),
        "convention": int(stats.convention),
        "error": int(stats.error),
        "fatal": int(stats.fatal),
        "info": int(stats.info),
        "refactor": int(stats.refactor),
        "statement": int(stats.statement),
        "warning": int(stats.warning),
    }


def run_pylint(path, modules):
    """
    PyLint evaluation : 10.0 - ((float(5 * error + warning + refactor + convention) / statement) * 10)
    """
    vals = {
        "by_module": {},
        "messages": {},
        "global_note": False,
        "global_stats": {},
    }

    # Run globally once

    pylint_output = StringIO()
    reporter = TextReporter(pylint_output)
    results = Run([path], reporter=reporter, exit=False)

    stats = results.linter.stats

    vals["global_stats"] = _prepare_stats(results.linter.stats)
    vals["global_note"] = stats.global_note

    # Run one by one
    for name in modules:
        mod_path = os.path.join(path, name)

        pylint_output = StringIO()
        reporter = TextReporter(pylint_output)
        results = Run([mod_path], reporter=reporter, exit=False)

        stats = results.linter.stats
        # output = pylint_output.getvalue()

        vals["by_module"][name] = _prepare_stats(stats)
        vals["messages"][name] = stats.by_msg

    return vals


def run_pylint_once(path):
    # name = os.path.basename(path)

    out_stream = StringIO()
    quiet_reporter = JSONReporter()
    quiet_reporter.set_output(out_stream)

    results = Run([path], reporter=quiet_reporter, do_exit=False)

    stats = results.linter.stats
    messages = pd.DataFrame(quiet_reporter.messages)
    # console.print(messages)

    vals = {
        "score": round_float(stats.global_note),
        "by_module": _prepare_stats(stats),
        "stats": stats.by_msg,
        "messages": messages,
    }

    return vals
