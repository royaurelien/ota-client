# -*- coding: utf-8 -*-
#!/bin/python3

from functools import lru_cache
import os
import shutil
import json

from pydantic import BaseSettings, validator
from pydantic.error_wrappers import ValidationError

from ota.core.console import console
from ota.core.tools import read_from_json, get_config_file, save_to_json


class Settings(BaseSettings):
    version: str = "0.1.0"

    url: str = "http://127.0.0.1:8080"
    auth_enable: bool = False
    auth_method: str = None

    threshold: float = 7.0

    @validator("threshold")
    @classmethod  # Optional, but your linter may like it.
    def check_storage_type(cls, value):
        if not isinstance(value, float) and value > 0:
            raise ValueError("Storage type can only be SSD or HDD.")
        return value

    @classmethod
    def new_file(cls, save=True):
        self = cls()
        if save:
            self.save()

        return self

    @classmethod
    def load_from_json(cls):
        filepath = get_config_file()

        if not os.path.exists(filepath):
            return cls.new_file()

        data = read_from_json(filepath)
        if not data:
            return cls.new_file()

        try:
            self = cls.parse_raw(data)
        except ValidationError as error:
            console.log(error)

            for item in error.errors():
                for key in item.get("loc"):
                    if key in data:
                        data.pop(key)
                self = cls.parse_raw(data)

        return self

    def save(self):
        data = self.json()
        console.print(data)
        filepath = get_config_file()
        save_to_json(filepath, data)

    def set_value(self, name, value, auto_save=True):
        self.__dict__[name] = value

        if auto_save:
            self.save()

    def get_value(self, name):
        try:
            value = getattr(self, name)
        except AttributeError:
            value = f"Unknown variable '{name}'"
        return self.__dict__.get(name)


@lru_cache()
def get_settings():
    return Settings.load_from_json()
