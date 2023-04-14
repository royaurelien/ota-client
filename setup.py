from setuptools import setup, find_packages

setup(
    name="ota",
    version="0.1.0",
    description="Odoo Technical Analysis",
    url="https://github.com/royaurelien/ota-client",
    author="Aurelien ROY",
    author_email="roy.aurelien@gmail.com",
    license="BSD 2-clause",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "odoo_analyse",
        "pylint",
        "requests",
        "sh",
        "cloc",
        "mccabe",
        "rich",
        "tabulate",
    ],
    extras_require={"graph": ["graphviz", "psycopg2"]},
    entry_points={
        "console_scripts": [
            "ota = ota.main:cli",
        ],
    },
)
