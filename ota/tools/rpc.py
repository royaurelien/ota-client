from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta


import xmlrpc.client
import pandas as pd

DEFAULT_MODELS = {
    "sale_management": "sale.order",
    "account": "account.move",
    "stock": "stock.picking",
    # "account_accountant": "",
    "purchase": "purchase.order",
    "crm": "crm.lead",
    # "web_studio": "",
    # "documents": "",
    # "hr_holidays": "",
    # "hr": "hr.employee",
    # "sign": "",
    "contacts": "res.partner",
    # "calendar": "",
    # "hr_contract": "",
}


def ftime(dt_obj):
    return dt_obj.strftime("%Y-%m-%d")


def get_periods():
    # now = datetime.now()
    now = date.today()

    yesterday = now - relativedelta(days=1)
    last_week = yesterday - relativedelta(weeks=1)
    last_month = yesterday - relativedelta(months=1)

    return (ftime(yesterday), ftime(last_week), ftime(last_month))


def get_create_domain(start_date, end_date):
    return [["create_date", ">=", start_date], ["create_date", "<=", end_date]]


class OdooRpc:
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

    def __str__(self) -> str:
        return f"<{self.db}>"

    def authenticate(self):
        try:
            self.uid = self.common.authenticate(
                self.db, self.username, self.password, {}
            )
        except Exception as error:
            # print(error)
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

    def get_records(self, model):
        res = self.execute(
            "ir.module.module",
            "search_read",
            [["state", "=", "installed"]],
            {"fields": ["name", "shortdesc"]},
        )
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
