from collections import namedtuple

from pydantic import BaseModel
from typing import Tuple
import pandas as pd

Columns = namedtuple(
    "Columns",
    [
        "name",
        "integer",
        "primary_integer",
        "text_right",
        "text_center",
        "text_left",
    ],
)

Options = namedtuple(
    "Options",
    ["url", "auth_enable", "auth_method"],
)

File = namedtuple(
    "File",
    ["name", "path", "content"],
)


class LinesOfCode(BaseModel):
    version: str = "0.0"
    exec_time: float
    languages: list
    data: dict
    lines: dict
    files: dict

    @property
    def languages_count(self):
        return len(self.languages)

    def get_dataframe(self):
        return pd.DataFrame(self.data)

    def get_summary(self):
        def format(lang):
            return f"{lang}: {self.lines[lang]} lines ({self.files[lang]})"

        return [format(lang) for lang in self.languages]


class LocalModule(BaseModel):
    record_count: int = 0
    depends: list
    fields: int = 0
    imports: list
    model_count: int = 0
    refers: list
    path: str
    language: dict = {}
    license: str = ""
    author: str = ""
    category: str = ""
    version: str = ""
    status: list = []
    name: str
    duration: float = 0.0
    manifest: dict
    models: dict
    classes: dict
    views: dict
    records: dict
    files: list
    # words: list
    hashsum: str
    readme: str
    readme_type: str = None
    info: dict
    models_count: str
    class_count: str
    records_count: str
    views_count: str
    depends_count: str
    PY: str
    XML: str
    JS: str
    missing_dependency: list = []
    score: float = 0.0

    def to_dict(self):
        return {self.name: vars(self)}


class LinterResult(BaseModel):
    name: str
    score: float
    stats: dict
    by_messages: dict
    messages: dict = {}
    report: dict = {}
    duplicates: list = []

    @property
    def has_duplicates(self):
        return bool(self.duplicates)

    @property
    def duplicates_count(self):
        return len(self.duplicates)

    def get_dataframe(self):
        return pd.DataFrame(self.messages)

    def get_summary(self):
        vals = {
            "score": self.score,
            "stats": self.stats,
            "by_messages": self.by_messages,
            "duplicates_count": self.duplicates_count,
        }

        return vals
