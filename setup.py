from setuptools import find_packages, setup

setup(
    name="odoo-technical-analysis",
    version="0.1.5",
    description="Odoo Technical Analysis",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/royaurelien/ota-client",
    author="Aurelien ROY",
    author_email="roy.aurelien@gmail.com",
    license="BSD 2-clause",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
        "pylint-odoo>=8.0.19",
        "pylint==2.15.5",
        "odoo-analyse>=1.3.0",
        "requests",
        "sh>=2.0.0",
        "rich",
        "black",
        "pydantic",
        "pydantic-settings",
        "pandas",
        "numpy",
        "appdirs",
        "jinja2",
    ],
    extras_require={},
    entry_points={
        "console_scripts": [
            "ota = ota.main:cli",
        ],
    },
)
