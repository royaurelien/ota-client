# -*- coding: utf-8 -*-
#!/bin/python3

import json
import requests
from urllib.parse import urljoin
import re

# requests.packages.urllib3.disable_warnings()


def download_file(url, params={}):

    with requests.get(url, params=params, stream=True) as response:
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            print(error)
            return False

        print(response.headers)

        d = response.headers["content-disposition"]
        fname = re.findall("filename=(.+)", d)[0]
        filepath = f"./{fname}" if fname else "./download"

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)


def send_analysis(url, data):
    try:
        response = requests.post(url, json=data)
    except requests.exceptions.HTTPError as error:
        print(response.status_code)
        return (response.status_code, {})

    return (response.status_code, response.json())
