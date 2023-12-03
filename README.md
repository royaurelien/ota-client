
# Odoo Technical Analysis

_**OTA** Command Line Tool_

![PyPI](https://img.shields.io/pypi/v/odoo-technical-analysis) ![PyPI](https://img.shields.io/pypi/pyversions/odoo-technical-analysis)


## Installation

Install from PyPI:
```bash
pip install odoo-technical-analysis
```

## Quickstart


### Analyze
`path` is the local repository you want to inspect.
```bash
ota analyze <path> --save
```

### Send report
```bash
ota send <json_file> --local

ID=$(ota send <json_file> --local)
```

### Download reports
* PDF Report :
```bash
ota download "$ID" pdf --template default --local
```
* Document :
```bash
ota download "$ID" docx --template doc --local
```
