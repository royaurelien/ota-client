import xmlrpc.client
import pandas as pd

from ota.core.tools import get_periods


def get_create_domain(start_date, end_date):
    return [["create_date", ">=", start_date], ["create_date", "<=", end_date]]


class OdooRpc:
    version: str = False

    def __init__(self, url, database, username, password):
        self.url = url
        self.db = database
        self.username = username
        self.password = password
        self.uid = None

        self.authenticate()

    @property
    def common(self):
        return xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")

    @property
    def models(self):
        return xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    @property
    def odoo_version(self):
        return self.version.get("server_serie", "0.0")

    def __str__(self) -> str:
        return f"<{self.db}>"

    def authenticate(self):
        try:
            self.version = self.common.version()
            self.uid = self.common.authenticate(
                self.db, self.username, self.password, {}
            )
        except Exception:
            self.uid = None

    @property
    def is_connected(self):
        return bool(self.uid)

    def execute(self, model, method, domain=[], options={}):
        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            method,
            [domain],
            options,
        )

    def _get_dataframe(self, model, method, domain=[], options={}):
        res = self.execute(model, method, domain, options)
        df = pd.DataFrame(res)
        df.sort_values("name", ascending=True, inplace=True)

        return (df, len(df))

    def get_applications(self):
        return self._get_dataframe(
            "ir.module.module",
            "search_read",
            [["state", "=", "installed"], ["application", "=", True]],
            {"fields": ["name", "shortdesc"]},
        )

    def get_modules(self):
        return self._get_dataframe(
            "ir.module.module",
            "search_read",
            [["state", "=", "installed"]],
            {"fields": ["name", "shortdesc", "author"]},
        )

    def get_parameters(self):
        keys = [
            "database.create_date",
            "database.expiration_date",
            "database.expiration_reason",
            # "database.secret",
            # "database.uuid",
        ]

        res = self.execute(
            "ir.config_parameter",
            "search_read",
            [("key", "in", keys)],
            {"fields": ["key", "value"]},
        )

        res = {item["key"]: item["value"] for item in res}

        return res.items()

    def get_meta(self):
        keys = {
            "models": "ir.model",
            "fields": "ir.model.fields",
            "views": "ir.ui.view",
            "menu": "ir.ui.menu",
            "actions": "ir.actions.actions",
            "act_server": "ir.actions.server",
            "act_report": "ir.actions.report",
            "cron": "ir.cron",
            "automation": "base.automation",
        }

        # res = {k: self.execute(v, "search_count", []) for k, v in keys.items()}

        res = [
            {"name": k, "count": self.execute(v, "search_count", [])}
            for k, v in keys.items()
        ]
        df = pd.DataFrame(res)

        return df

    def get_stats(self, model):
        vals = {
            "by_day": None,
            "top_creators": None,
        }
        yesterday, last_week, last_month = get_periods()

        domain = get_create_domain(last_week, yesterday)

        options = {"fields": ["create_uid", "create_date"]}

        vals["total"] = self.execute(model, "search_count", [])
        vals["this_week"] = self.execute(
            model, "search_count", get_create_domain(last_week, yesterday)
        )
        vals["this_month"] = self.execute(
            model, "search_count", get_create_domain(last_month, yesterday)
        )
        vals["yesterday"] = self.execute(
            model, "search_count", get_create_domain(yesterday, yesterday)
        )

        res = self.execute(model, "search_read", domain, options)

        df = pd.DataFrame(res)

        if not vals["this_week"]:
            return vals

        df["create_uid"] = df["create_uid"].apply(
            lambda row: row[1] if isinstance(row, list) else row
        )
        df["create_date"] = pd.to_datetime(df["create_date"])
        df["day_name"] = df["create_date"].dt.day_name()
        df["month_name"] = df["create_date"].dt.month_name()
        df["month_name"] = df["create_date"].dt.month_name()
        df["week"] = df["create_date"].dt.isocalendar().week

        # By day
        df1 = (
            df.groupby(pd.Grouper(key="create_date", axis=0, freq="D"))["create_uid"]
            .count()
            .to_frame(name="count")
        )
        df1.reset_index(inplace=True)
        df1["create_date"] = pd.to_datetime(df1["create_date"]).dt.date
        df1.set_index(["create_date"], inplace=True)
        vals["by_day"] = df1.transpose()

        df2 = (
            df.groupby(["create_uid"])
            .count()["id"]
            .sort_values(ascending=False)
            .to_frame(name="count")
        )
        df2.reset_index(inplace=True)
        # df2.rename(columns={"create_uid", "name"}, inplace=True)
        vals["top_creators"] = df2

        return vals
