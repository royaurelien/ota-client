import os
from functools import lru_cache

from appdirs import AppDirs
from pydantic import ValidationError
from pydantic_settings import BaseSettings

from ota.core.console import console
from ota.core.tools import ROOT_DIR, save_to

CONFIG_FILENAME = "config.json"
DIRS = AppDirs("ota", "Aurelien ROY")


def init_dirs():
    os.makedirs(DIRS.user_data_dir, exist_ok=True)
    # console.log(ROOT_DIR)


def get_config_path():
    return DIRS.user_data_dir


def get_config_filepath():
    return os.path.join(get_config_path(), CONFIG_FILENAME)


init_dirs()


class Settings(BaseSettings):
    version: str = "0.1.0"

    url: str = "http://127.0.0.1:8080"
    local_url: str = "http://0.0.0.0:8080"
    api_version: str = "v1"
    api_report_url: str = f"/{api_version}/report"
    api_analyze_url: str = f"/{api_version}/analyze"
    auth_enable: bool = False
    auth_method: None = None
    digits: int = 2
    threshold: float = 7.0
    models_by_applications: dict = {
        "sale_management": "sale.order",
        "account": "account.move",
        "stock": "stock.picking",
        "account_accountant": "account.move",
        "purchase": "purchase.order",
        "crm": "crm.lead",
        "documents": "documents.document",
        # "web_studio": "",
        # "hr_holidays": "",
        # "hr": "hr.employee",
        # "sign": "",
        "contacts": "res.partner",
        # "calendar": "",
        # "hr_contract": "",
    }
    local_database: str = "http://localhost:8069"
    local_user: str = "admin"
    local_password: str = "admin"

    def get_local_credentials(self):
        """Return local database credentials"""
        return (self.local_database, self.local_user, self.local_password)

    @classmethod
    def new_file(cls, save=True):
        """Get defaults settings and save"""
        self = cls()
        if save:
            self.save()

        return self

    @classmethod
    def load_from_json(cls):
        """Load settings from JSON file"""
        filepath = get_config_filepath()

        if not os.path.exists(filepath):
            return cls.new_file()

        with open(filepath) as file:
            data = file.read()

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

        self.save()
        return self

    def save(self, clear=False):
        """Save settings to JSON file"""
        data = self.json()
        filepath = get_config_filepath()

        if clear and os.path.exists(filepath):
            os.remove(filepath)

        save_to(data, filepath)

    def set_value(self, name, value, auto_save=True):
        """Set value"""
        self.__dict__[name] = value

        if auto_save:
            self.save()

    def get_value(self, name):
        """Get value"""
        try:
            value = getattr(self, name)
        except AttributeError:
            value = f"<Unknown variable '{name}'>"
        return value


@lru_cache()
def get_settings():
    return Settings.load_from_json()
