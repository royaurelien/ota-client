from setuptools import setup, find_packages

setup(
    name="ota",
    version="0.0.5",
    description="Odoo Technical Analysis",
    url="https://github.com/royaurelien/ota-client",
    author="Aurelien ROY",
    author_email="roy.aurelien@gmail.com",
    license="BSD 2-clause",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "odoo-analyse",
        "pylint",
        "requests",
        "sh",
        "rich",
        "black",
        "pylint-odoo",
        "pydantic",
        "pandas",
        "numpy",
        "appdirs",
    ],
    extras_require={},
    entry_points={
        "console_scripts": [
            "ota = ota.main:cli",
        ],
    },
)
