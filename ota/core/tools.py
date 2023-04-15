import json
import requests
from urllib.parse import urljoin
import re
import os
from pathlib import Path

# requests.packages.urllib3.disable_warnings()

from ota.core.console import console, Table


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


def read_from_json(path):
    """Load JSON File from path"""
    with open(path, "r") as file:
        try:
            data = json.load(file)
        except json.decoder.JSONDecodeError:
            data = None

    return data


def save_to_json(path, data):
    """Dump dict to JSON file"""
    with open(path, "w") as file:
        file.write(json.dumps(data))


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


def dataframe_to_table(df, title, columns, **kwargs):
    table = Table(title=title)
    df = df[columns]

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
