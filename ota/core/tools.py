import ast
from datetime import datetime
import json
import requests
from urllib.parse import urljoin
import re
import os
from pathlib import Path
from io import StringIO
import sys

from pylint import __version__ as PYLINT_VERSION
from pylint.lint import Run
from pylint.reporters.text import TextReporter
from pylint.reporters import JSONReporter
import pandas as pd
from black import format_str, FileMode
from black.parsing import InvalidInput
import jinja2
from jinja2.exceptions import UndefinedError

# requests.packages.urllib3.disable_warnings()

from ota.core.console import console, Table
from ota.core.models import File, LinterResult


def dict_to_list(data, keys=None):
    def function(item):
        return f'{item}="{data[item]}"'

    if keys:
        items = filter(lambda x: x in keys, data)
    else:
        items = data

    return list(map(function, items))


def get_keyword(obj):
    name = obj.arg
    value = obj.value

    if isinstance(value, ast.Constant):
        value = value.value

    return (name, value)


def get_assign(src):
    def function(obj):
        for child in obj.body:
            if isinstance(child, ast.ClassDef):
                return function(child)
            if isinstance(child, ast.Assign):
                return child

    # src = format_str(src, mode=FileMode())
    src = src.strip('"')
    # print(src)
    obj = ast.parse(src)
    return function(obj)


def generate(template: str, data: dict, filename: str, functions=None) -> File:
    code = generate_code(template, data, functions)
    file = generate_file(filename, code)

    return file


def generate_code(template: str, data: dict, functions=None) -> str:
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
    jinja_template = jinja_env.get_template(template)

    if functions:
        jinja_template.globals.update(functions)

    try:
        code = jinja_template.render(**data)
        code = format_str(code, mode=FileMode())
    except UndefinedError as error:
        _logger.error(error)
        code = False
    except InvalidInput as error:
        _logger.error(error)
        exit(1)

    return code


def generate_file(filename: str, content: str) -> File:
    filepath = f"{filename}.py"

    return File(name=filename, path=filepath, content=content)


def get_arg(obj):
    value = obj

    if isinstance(value, ast.Constant):
        value = value.value
    elif isinstance(value, ast.List):
        result = []

        for child in value.elts:
            res = []
            if isinstance(child, ast.Tuple):
                for cc in child.elts:
                    if isinstance(cc, ast.Constant):
                        res.append(cc.value)
                        continue
                    if isinstance(cc, ast.Call):
                        tmp = f"{cc.func.id}({cc.args[0].value})"
                        res.append(tmp)
                        continue
            result.append(res)
        # print(result)
        value = ast.dump(value)

        # value = ast.literal_eval(value)

        # print(value)
        # exit(1)
    # else:
    #     print(type(obj))
    #     exit(1)

    # return f'"{value}"'
    return value


def get_config_file():
    parts = [Path.home(), ".config", "odoo-technical-analysis.json"]
    return os.path.join(*parts)


def humanize(string):
    """Humanize string"""

    if "count" in string and len(string.split("count")) > 1:
        string = string.replace("count", "")

    string = string.replace("_", " ")
    string = string.strip()
    string = string.capitalize()

    return string


def download_file(url, params=None):
    """Download file"""

    if not params:
        params = {}

    with requests.get(url, params=params, stream=True, timeout=60) as response:
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            console.log(error)
            return False

        console.log(response.headers)

        content_disposition = response.headers["content-disposition"]
        fname = re.findall("filename=(.+)", content_disposition)[0]
        filepath = f"./{fname}" if fname else "./download"

        with open(filepath, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)


def send_analysis(url, data):
    """Post File"""
    try:
        response = requests.post(url, json=data, timeout=60)
    except requests.exceptions.HTTPError as error:
        console.log(error)

        return (False, {})

    return (response.status_code, response.json())


def dataframe_to_table(df, title, columns=[], **kwargs):
    table = Table(title=title)

    if not columns:
        columns = list(df.columns)
    else:
        df = df[columns]

    df = df.astype(str)

    options = kwargs.get("column_options", {})

    for name, title in zip(columns, map(humanize, list(df))):
        column_options = options.get(name, {})
        table.add_column(title, **column_options)

    data = df.to_dict(orient="split")

    for line in data["data"]:
        table.add_row(*line)

    return table


# def dict_to_table(vals_list, title, columns=[], **kwargs):
#     table = Table(title=title)
#     options = kwargs.get("column_options", {})

#     if not columns:
#         columns = list(vals_list[0].keys())

#     print(columns)

#     for name, title in zip(columns, map(humanize, columns)):
#         column_options = options.get(name, {})
#         table.add_column(title, **column_options)

#     for vals in vals_list:
#         values = [str(v) for k, v in vals.items() if k in columns]
#         print(values)
#         table.add_row(*values)


class JSONSetEncoder(json.JSONEncoder):
    """Custom JSON Encoder to transform python sets into simple list"""

    def default(self, o):  # pylint: disable=E0202
        if isinstance(o, set):
            return list(o)
        return super(JSONSetEncoder, self).default(o)


def load_from_json(filepath):
    """Load JSON File from path"""
    with open(filepath, "r") as file:
        try:
            data = json.load(file)
        except json.decoder.JSONDecodeError:
            data = None

    return data


def to_json(data):
    return json.dumps(data, cls=JSONSetEncoder, indent=2)


def save_to(data, filepath):
    with open(filepath, "w") as file:
        file.write(data)


def save_to_json(data, filepath):
    json_object = json.dumps(data, cls=JSONSetEncoder, indent=2)

    with open(filepath, "w") as file:
        file.write(json_object)


def str_to_list(string):
    """Transform string to list"""
    if not string:
        return []
    return list(set(map(str.strip, string.split(","))))


def get_folder_name(path):
    return os.path.basename(path)


def round_float(value, digits=2):
    return round(value, digits)


def _prepare_stats(stats):
    return {
        # 'success': bool(stats.global_note >= threshold),
        # "score": round_float(stats.global_note),
        "convention": int(stats.convention),
        "error": int(stats.error),
        "fatal": int(stats.fatal),
        "info": int(stats.info),
        "refactor": int(stats.refactor),
        "statement": int(stats.statement),
        "warning": int(stats.warning),
    }


def run_pylint(path, **kwargs):
    """
    Run PyLint on path
    Evaluation : 10.0 - ((float(5 * error + warning + refactor + convention) / statement) * 10)
    """
    name = kwargs.get("name", os.path.basename(path))
    recursive = kwargs.get("recursive", False)

    out_stream = StringIO()
    quiet_reporter = JSONReporter()
    quiet_reporter.set_output(out_stream)

    args = [path, "-ry"]
    if recursive:
        args += ["--recursive", "y"]

    results = Run(args, reporter=quiet_reporter, do_exit=False)

    stats = results.linter.stats

    df = pd.DataFrame({name: stats.code_type_count}).transpose()
    df1 = df.copy()

    for key in ["code", "comment", "docstring", "empty"]:
        df1[key] = round(df1[key] * 100 / df1["total"], 2)

    vals = {
        "name": name,
        "score": round_float(stats.global_note),
        "stats": _prepare_stats(stats),
        "by_messages": stats.by_msg,
        "report": df1.to_dict(orient="records")[0],
    }

    messages = pd.DataFrame(quiet_reporter.messages)

    if not messages.empty:
        duplicate_code = messages[(messages["symbol"] == "duplicate-code")]

        # module.models.model --> models / model
        # messages["module"] = messages["module"].apply(
        #     lambda row: " / ".join(row.split(".")[-2:])
        # )

        messages.drop(duplicate_code.index, inplace=True)
        messages.sort_values(["module", "line"], ascending=True, inplace=True)

        def get_file(path):
            parts = path.split("/")
            length = 2 if len(parts) <= 2 else 3
            return "/".join(parts[-length:])

        messages["file"] = messages["path"].apply(get_file)

        keys = [
            "file",
            "msg_id",
            "symbol",
            "msg",
            "C",
            "category",
            # "confidence",
            # "abspath",
            # "path",
            "module",
            "obj",
            "line",
            "column",
            # "end_line",
            # "end_column",
        ]

        messages = messages[keys]
        vals.update(
            {
                "messages": messages.to_dict(),
                "duplicates": list(duplicate_code["msg"].values)
                if not duplicate_code.empty
                else [],
            }
        )

    return LinterResult(**vals)


def now():
    return datetime.now().strftime("%Y/%m/%d %H:%M:%S")
