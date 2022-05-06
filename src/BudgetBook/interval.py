import copy
import datetime
import pandas as pd
from typing import List
from dateutil.relativedelta import relativedelta
import enum

import plotly.graph_objects as go
import plotly.express as px

TIMEDELTA_FULL_YEAR = datetime.timedelta(days=365)

CURRENCY_SYMBOL = "Euro"


@enum.unique
class Category(enum.Enum):
    SALERY = 0
    UNKNOWN_INCOME = 1
    UNKNOWN = 2
    OTHER_PAYMENT = 3
    INSURANCE = 4
    MOBILITY = 5
    HOUSHOLD = 6
    TAX = 7


CATEGORY_TO_COLOR_MAP = {
    c.name: px.colors.qualitative.Plotly[idx] for idx, c in enumerate(Category)
}


class DatedMoneyTransfer:
    def __init__(
        self,
        name: str,
        desc: str,
        category: Category,
        date: datetime.date,
        amount: float,
    ) -> None:
        self._name = name
        self._desc = desc
        self._amount = amount
        self._date = date
        self._category = category

    def get_category(self) -> Category:
        return self._category

    def get_name(self) -> str:
        return self._name

    def get_desc(self) -> str:
        return self._desc

    def get_amount(self) -> float:
        return self._amount

    def get_date(self) -> datetime.date:
        return self._date

    def __str__(self) -> str:
        return f"{self._name}: {self._amount} {CURRENCY_SYMBOL} on {self._date}"

    def __repr__(self) -> str:
        return str(self)


class MoneyTransferInterval:
    def __init__(self, years: int = 0, months: int = 0, days: int = 0) -> None:
        if years == 0 and months == 0 and days == 0:
            raise AttributeError("Interval has to be larger than 0 days!")
        self._interval = relativedelta(years=years, months=months, days=days)

    def to_relative_delta(self) -> relativedelta:
        return self._interval

    @staticmethod
    def monthly():
        return MoneyTransferInterval(months=1)

    @staticmethod
    def quaterly():
        return MoneyTransferInterval(months=4)

    @staticmethod
    def yearly():
        return MoneyTransferInterval(years=1)

    @staticmethod
    def once():
        return None

    def __str__(self) -> str:
        s = []
        if self._interval.years > 0:
            s.append(f"{self._interval.years} years")
        if self._interval.months > 0:
            s.append(f"{self._interval.months} months")
        if self._interval.days > 0:
            s.append(f"{self._interval.days} days")

        return f"every {' and '.join(s)}"

    def __repr__(self) -> str:
        return str(self)


class ReocurringEvent:
    @staticmethod
    def once(d: datetime.date):
        return ReocurringEvent(first_occurence=d, interval_size=None)

    def __init__(
        self,
        first_occurence: datetime.date,
        interval_size: MoneyTransferInterval,
        last_occurence: datetime.date = None,
    ) -> None:
        self._first_occurence = first_occurence
        self._interval_size = interval_size
        self._last_occurence = last_occurence

    def __str__(self) -> str:
        if self._last_occurence is not None:
            if self._interval_size is not None:
                return f"{self._interval_size} from {self._first_occurence} to {self._last_occurence}"
            else:
                assert False
        else:
            if self._interval_size is not None:
                return f"{self._interval_size} starting from {self._first_occurence}"
            else:
                return f"on {self._first_occurence}"

    def __repr__(self) -> str:
        return str(self)

    def get_first_occurence(self) -> datetime.date:
        return self._first_occurence

    def get_last_occurence(self) -> datetime.date:
        return self._last_occurence

    def get_interval_size(self) -> MoneyTransferInterval:
        return self._interval_size

    def set_first_occurence(self, first_ocurrence: datetime.date):
        self._first_occurence = first_ocurrence

    def set_interval_size(self, interval_size: MoneyTransferInterval):
        self._interval_size = interval_size

    def set_last_occurence(self, last_ocurrence: datetime.date):
        self._last_occurence = last_ocurrence

    def iterate(self, from_date: datetime.date, up_to: datetime.date) -> datetime.date:
        current = max(from_date, self._first_occurence)

        last = self._last_occurence
        if up_to is not None:
            if last is not None:
                if last > up_to:
                    last = up_to
            else:
                last = up_to

        if last is None:
            raise AttributeError("No end date specified for reocurring event!")

        while current < last:
            yield current
            if self._interval_size is not None:
                current = current + self._interval_size.to_relative_delta()
            else:
                return


class ReocurringMoneyTransfer:
    def __init__(
        self,
        name: str,
        category: Category,
        money_transfer_amount: float,
        reocurrence: ReocurringEvent,
        desc: str = "",
    ) -> None:
        self._reocurrence = reocurrence
        self._money_transfer_amount = money_transfer_amount
        self._category = category
        self._name = name
        self._desc = desc

    def get_name(self) -> str:
        return self._name

    def get__desc(self) -> str:
        return self._desc

    def get_category(self) -> str:
        return self._category

    def get_money_transfer_amount(self) -> str:
        return self._money_transfer_amount

    def get_reocurrence(self) -> ReocurringEvent:
        return self._reocurrence

    def __str__(self) -> str:
        return f"{self._name}: {self._money_transfer_amount} {CURRENCY_SYMBOL} {self._reocurrence}"

    def __repr__(self) -> str:
        return str(self)

    def iterate(
        self, from_date: datetime.date, up_to: datetime.date
    ) -> DatedMoneyTransfer:
        for current_date in self._reocurrence.iterate(from_date=from_date, up_to=up_to):
            yield DatedMoneyTransfer(
                self._name,
                self._desc,
                self._category,
                current_date,
                self._money_transfer_amount,
            )


class ReocurringMoneyTransferBuilder:
    def __init__(self) -> None:
        self._current_recurrence = ReocurringEvent(None, None, None)
        self._scheduled_transfers = []
        self._current_category = Category.UNKNOWN

    def get_scheduled_transfers(self) -> List[ReocurringMoneyTransfer]:
        return self._scheduled_transfers

    def set_first_ocurrence(self, year: int) -> None:
        self._current_recurrence.set_first_occurence(
            datetime.date(year=year, month=1, day=1)
        )

    def set_last_ocurrence(self, year: int) -> None:
        self._current_recurrence.set_last_occurence(
            datetime.date(year=year, month=1, day=1)
        )

    def set_interval(self, years: int = 0, months: int = 0, days: int = 0) -> None:
        self._current_recurrence.set_interval_size(
            MoneyTransferInterval(years=years, months=months, days=days)
        )

    def set_interval_monthly(self) -> None:
        self._current_recurrence.set_interval_size(MoneyTransferInterval.monthly())

    def set_interval_quaterly(self) -> None:
        self._current_recurrence.set_interval_size(MoneyTransferInterval.quaterly())

    def set_interval_yearly(self) -> None:
        self._current_recurrence.set_interval_size(MoneyTransferInterval.yearly())

    def set_category(self, category: Category) -> None:
        self._current_category = category

    def schedule_money_transfer(self, name: str, amount: float):
        self._scheduled_transfers.append(
            ReocurringMoneyTransfer(
                name,
                self._current_category,
                amount,
                copy.copy(self._current_recurrence),
            )
        )

        return self._scheduled_transfers[-1]


class AccountStatementCsvParser:
    def __init__(self, csv_path):
        self._csv_path = csv_path
        self._csv_data = pd.read_csv(csv_path, sep=";")

        self._col_name_sender_receiver = "Name Zahlungsbeteiligter"
        self._col_amount = "Betrag"
        self._col_type_of_transer = "Buchungstext"
        self._col_transfer_desc = "Verwendungszweck"
        self._col_date = "Buchungstag"
        self._col_date_format = "%d.%m.%Y"

        self._csv_data[self._col_amount] = (
            self._csv_data[self._col_amount]
            .apply(lambda x: x.replace(",", "."))
            .astype(float)
        )

        self._csv_data[self._col_name_sender_receiver] = self._csv_data[
            self._col_name_sender_receiver
        ].astype(str)

        self._csv_data[self._col_transfer_desc] = self._csv_data[
            self._col_transfer_desc
        ].astype(str)

        self._csv_data[self._col_date] = pd.to_datetime(
            self._csv_data[self._col_date], format=self._col_date_format
        )

        self._preprocess()

    def _preprocess(self):
        self._unique_sender_receiver = self._csv_data[
            self._col_name_sender_receiver
        ].unique()

        self._unique_transfer_types = self._csv_data[self._col_type_of_transer].unique()

    def to_scheduled_transfers(self):
        scheduled_transfers = []
        for _, row in self._csv_data.iterrows():
            date_without_day = datetime.date(
                year=row[self._col_date].year, month=row[self._col_date].month, day=1
            )

            scheduled_transfers.append(
                ReocurringMoneyTransfer(
                    row[self._col_name_sender_receiver],
                    self._map_to_category(row),
                    row[self._col_amount],
                    ReocurringEvent.once(date_without_day),
                )
            )

        return scheduled_transfers

    def _map_to_category(self, row):
        def desc_contains(candiates):
            return any(v in row[self._col_transfer_desc].lower() for v in candiates)

        def sender_receiver_contains(candiates):
            return any(
                v in row[self._col_name_sender_receiver].lower() for v in candiates
            )

        if row[self._col_amount] > 0:
            if desc_contains(["lohn", "gehalt"]):
                return Category.SALERY
            else:
                return Category.UNKNOWN_INCOME
        else:
            if sender_receiver_contains(["versicherung", "assuranc"]):
                return Category.INSURANCE
            elif desc_contains(
                ["tank", "park", "garage", "autohaus"]
            ) or sender_receiver_contains(["tank"]):
                return Category.MOBILITY
            elif sender_receiver_contains(
                ["lidl", "rewe", "finkbeiner", "ecenter"]
            ) or desc_contains(["miet", "rewe", "finkbeiner", "takeaway", "lidl"]):
                return Category.HOUSHOLD
            elif desc_contains(["steuer"]):
                return Category.TAX
            else:
                return Category.OTHER_PAYMENT

        return Category.UNKNOWN


class MoneyTransferManager:
    def __init__(self) -> None:
        self._scheduled_transfers: List[ReocurringMoneyTransfer] = []
        self._from_date = None
        self._to_date = None
        self._dataframe_cache = None

    def add_transfer(self, transfer: ReocurringMoneyTransfer):
        self._scheduled_transfers.append(transfer)

    def add_transfers(self, transfers: List[ReocurringMoneyTransfer]):
        self._scheduled_transfers.extend(transfers)

    def get_first_transfer_date(self) -> datetime.date:
        return min(
            d.get_reocurrence().get_first_occurence() for d in self._scheduled_transfers
        )

    def set_analysis_interval(self, from_date, to_date):
        self._from_date = from_date
        self._to_date = to_date
        self._to_dataframe()

    def _to_dataframe(self):
        indivdual_transfers = []

        for scheduled_transfer in self._scheduled_transfers:
            transfers = [
                (
                    transfer.get_date(),
                    transfer.get_category().name,
                    transfer.get_name(),
                    transfer.get_desc(),
                    transfer.get_amount(),
                )
                for transfer in scheduled_transfer.iterate(
                    from_date=self._from_date, up_to=self._to_date
                )
            ]
            indivdual_transfers.extend(transfers)

        self._dataframe_cache = pd.DataFrame(
            indivdual_transfers, columns=["date", "category", "name", "desc", "amount"]
        )
        self._dataframe_cache["category"] = [
            str(s) for s in self._dataframe_cache["category"]
        ]
        self._dataframe_cache["date"] = pd.to_datetime(self._dataframe_cache["date"])
        self._dataframe_cache.set_index("date", inplace=True)

    def plot_payments_per_month(self):
        df = self._dataframe_cache.reset_index()
        df = df[df["amount"] < 0]
        df["amount"] = -df["amount"]

        fig = go.Figure()

        for category in df["category"].unique():
            mask = df["category"] == category
            curr_df = df[mask]
            fig.add_trace(
                go.Bar(
                    name=category,
                    x=curr_df["date"],
                    y=curr_df["amount"],
                    text=[v[:20] for v in curr_df["name"]],
                    marker_color=CATEGORY_TO_COLOR_MAP[category],
                    hovertemplate=f"%{{y:.2f}} {CURRENCY_SYMBOL}<br>%{{x}}<br>%{{text}}<extra>{category}</extra>",
                ),
            )
        fig.update_layout(barmode="stack", title="Payments Per Month")

        return fig

    def plot_balance_per_month(self):
        fig = go.Figure()
        average_balance_per_month = (
            self._dataframe_cache["amount"].groupby(by=pd.Grouper(freq="M")).sum()
        )
        average_balance_per_month.index = pd.DatetimeIndex(
            datetime.date(year=d.year, month=d.month, day=1)
            for d in average_balance_per_month.index
        )
        fig.add_trace(
            go.Scatter(
                name="Average",
                x=average_balance_per_month.index,
                y=average_balance_per_month,
                hovertemplate=f"%{{y:.2f}} {CURRENCY_SYMBOL}<br>%{{x}}<extra></extra>",
            ),
        )

        fig.update_layout(barmode="group", title="Balance Per Month")

        return fig

    def plot_transfers_per_month(self):
        df = (
            self._dataframe_cache.reset_index()
            .groupby(["date", "category"])
            .sum()
            .reset_index()
        )

        fig = go.Figure()

        for category in df["category"].unique():
            mask = df["category"] == category
            curr_df = df[mask]
            fig.add_trace(
                go.Bar(
                    name=category,
                    x=curr_df["date"],
                    y=curr_df["amount"],
                    marker_color=CATEGORY_TO_COLOR_MAP[category],
                    hovertemplate=f"%{{y:.2f}} {CURRENCY_SYMBOL}<br>%{{x}}<extra>{category}</extra>",
                ),
            )
        fig.update_layout(barmode="group", title="Transfers Per Month")
        return fig

    def plot_pie_chart_per_cateogry(self):
        grouped_per_category = self._dataframe_cache[
            self._dataframe_cache["amount"] < 0
        ].groupby(by="category")
        amount_per_category = grouped_per_category["amount"].sum().abs()

        fig = go.Figure()
        fig.add_trace(
            go.Pie(
                values=amount_per_category,
                labels=amount_per_category.index,
            )
        )
        fig.update_traces(
            marker=dict(
                colors=[CATEGORY_TO_COLOR_MAP[c] for c in amount_per_category.index]
            )
        )
        fig.update_layout(title="Payments per Category")
        return fig
