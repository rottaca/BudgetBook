import datetime
from typing import List
import numpy as np
from dateutil import relativedelta

import pandas as pd
import plotly.graph_objects as go

from BudgetBook.dated_transaction import DatedTransaction
from BudgetBook.regular_transaction import RegularTransaction
from BudgetBook.config_parser import (
    ConfigParser,
    DataColumns,
    DATA_COLUMN_TO_DISPLAY_NAME,
)
from BudgetBook.helper import COLORMAP, CURRENCY_SYMBOL


class TransactionVisualizer:
    def __init__(self, config: ConfigParser) -> None:
        self._scheduled_transactions: List[RegularTransaction] = []
        self._from_date = None
        self._to_date = None
        self._dataframe_cache = None
        self._config = config

    def clear_transactions(self):
        self._scheduled_transactions.clear()
        self._dataframe_cache = None
        self._from_date = None
        self._to_date = None

    def add_transaction(self, transaction: RegularTransaction):
        self._scheduled_transactions.append(transaction)

    def add_transactions(self, transactions: List[RegularTransaction]):
        self._scheduled_transactions.extend(transactions)

    def get_transactions(self):
        return self._scheduled_transactions

    def set_analysis_interval(self, from_date, to_date):
        self._from_date = from_date
        self._to_date = to_date
        self._to_dataframe()

        if self.dataset_is_valid():
            self.category_to_color_map = {
                c: COLORMAP[idx]
                for idx, c in enumerate(
                    self._dataframe_cache[DataColumns.CATEGORY].unique()
                )
            }

    def dataset_is_valid(self):
        return self._dataframe_cache is not None

    def get_dataframe(self):
        return self._dataframe_cache

    def get_first_transaction_date_in_analysis_interval(self):
        return self._dataframe_cache.index.min()

    def get_last_transaction_date_in_analysis_interval(self):
        return self._dataframe_cache.index.max()

    def _to_dataframe(self):
        if len(self._scheduled_transactions) == 0:
            self._dataframe_cache = None
            return

        indivdual_transactions = []

        for scheduled_transaction in self._scheduled_transactions:
            if isinstance(scheduled_transaction, RegularTransaction):
                transactions = [
                    transaction.to_dict()
                    for transaction in scheduled_transaction.iterate(
                        from_date=self._from_date, up_to=self._to_date
                    )
                ]
                indivdual_transactions.extend(transactions)
            elif isinstance(scheduled_transaction, DatedTransaction):
                if (
                    scheduled_transaction.date >= self._from_date
                    and scheduled_transaction.date < self._to_date
                ):
                    indivdual_transactions.append(scheduled_transaction.to_dict())
            else:
                raise AttributeError("Invalid type")

        self._dataframe_cache = pd.DataFrame.from_records(
            indivdual_transactions,
        )

        self._dataframe_cache.set_index(DataColumns.DATE, inplace=True)
        self._dataframe_cache.index = pd.DatetimeIndex(self._dataframe_cache.index)
        self._dataframe_cache.sort_index(inplace=True)

        self._dataframe_cache["date_without_day"] = [
            datetime.date(year=d.year, month=d.month, day=1)
            for d in self._dataframe_cache.index
        ]

    def plot_statement_dataframe(self):

        if not self.dataset_is_valid():
            return pd.DataFrame()

        df = self._dataframe_cache.reset_index()
        df = df[
            [
                DataColumns.DATE,
                DataColumns.PAYMENT_PARTY,
                DataColumns.AMOUNT,
                DataColumns.DESCRIPTION,
                DataColumns.CATEGORY,
            ]
        ]
        df[DataColumns.DATE] = df[DataColumns.DATE].dt.strftime("%Y-%m-%d")

        df = df.rename(columns=DATA_COLUMN_TO_DISPLAY_NAME)

        return df

    def _plot_stacked_by_category_per_month(self, df, amount, title, yaxis_title):
        fig = go.Figure()

        sum_per_month = amount.groupby(by=pd.Grouper(freq="M")).sum()
        dates = [
            datetime.date(year=d.year, month=d.month, day=1)
            for d in sum_per_month.index
        ]
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=sum_per_month.values,
                name="Total Sum",
                mode="lines+markers",
                marker_color="black",
                line_dash="dash",
                hovertemplate=f"%{{y:.2f}} {CURRENCY_SYMBOL}<br>%{{x}}<extra></extra>",
            )
        )

        for category in df[DataColumns.CATEGORY].unique():
            mask = df[DataColumns.CATEGORY] == category
            curr_df = df[mask]
            curr_amount = amount[mask]
            fig.add_trace(
                go.Bar(
                    name=category,
                    x=curr_df["date_without_day"],
                    y=curr_amount,
                    text=[
                        f"{date:%d.%m.%Y}<br>{d[DataColumns.PAYMENT_PARTY][:40]}"
                        for date, d in curr_df.iterrows()
                    ],
                    marker_color=self.category_to_color_map[category],
                    hovertemplate=f"%{{y:.2f}} {CURRENCY_SYMBOL}<br>%{{text}}<extra>{category}</extra>",
                ),
            )

        fig.update_layout(
            barmode="relative",
            title=title,
            xaxis_title="[Date]",
            yaxis_title=yaxis_title,
            showlegend=True,
        )
        return fig

    def plot_payments_per_month(self):
        if not self.dataset_is_valid():
            return go.Figure()

        df = self._get_data_without_internal_transactions()

        df = df[df[DataColumns.AMOUNT] < 0]
        abs_amount = df[DataColumns.AMOUNT].abs()

        return self._plot_stacked_by_category_per_month(
            df,
            abs_amount,
            title="Payments Per Month",
            yaxis_title=f"Payments Per Month [{CURRENCY_SYMBOL}]",
        )

    def plot_internal_transactions_per_month(self):

        if not self.dataset_is_valid():
            return go.Figure()

        df = self._get_internal_transactions()

        return self._plot_stacked_by_category_per_month(
            df,
            df[DataColumns.AMOUNT],
            title="Internal Transfers Per Month",
            yaxis_title=f"Internal Transfers Per Month [{CURRENCY_SYMBOL}]",
        )

    def plot_income_per_month(self):
        if not self.dataset_is_valid():
            return go.Figure()

        df = self._get_data_without_internal_transactions()
        df = df[df[DataColumns.AMOUNT] > 0]

        return self._plot_stacked_by_category_per_month(
            df,
            df[DataColumns.AMOUNT],
            title="Income Per Month",
            yaxis_title=f"Income Per Month [{CURRENCY_SYMBOL}]",
        )

    def plot_balance_per_month(self):

        if not self.dataset_is_valid():
            return go.Figure()

        average_balance_per_month = self._dataframe_cache[DataColumns.AMOUNT].cumsum()

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=average_balance_per_month.index,
                y=average_balance_per_month,
                hovertemplate=f"%{{y:.2f}} {CURRENCY_SYMBOL}<br>%{{x}}<extra></extra>",
            ),
        )

        fig.update_layout(
            barmode="group",
            title="Balance Per Month",
            xaxis_title="[Date]",
            yaxis_title=f"Balance Relative to Dataset Start [{CURRENCY_SYMBOL}]",
        )

        return fig

    def plot_transactions_per_month(self):

        if not self.dataset_is_valid():
            return go.Figure()

        df = (
            self._dataframe_cache.groupby(["date_without_day", DataColumns.CATEGORY])
            .sum()
            .reset_index()
        )

        fig = go.Figure()

        for category in df[DataColumns.CATEGORY].unique():
            mask = df[DataColumns.CATEGORY] == category
            curr_df = df[mask]
            fig.add_trace(
                go.Bar(
                    name=category,
                    x=curr_df["date_without_day"],
                    y=curr_df[DataColumns.AMOUNT],
                    marker_color=self.category_to_color_map[category],
                    hovertemplate=f"%{{y:.2f}} {CURRENCY_SYMBOL}<br>%{{x}}<extra>{category}</extra>",
                ),
            )
        fig.update_layout(
            barmode="group",
            title="Transfers Per Month",
            xaxis_title="[Date]",
            yaxis_title=f"Transfers Per Month [{CURRENCY_SYMBOL}]",
        )
        return fig

    def _get_data_without_internal_transactions(self):
        internal_transaction_categories = (
            self._config.get_internal_transaction_categories()
        )
        mask = self._dataframe_cache[DataColumns.CATEGORY].isin(
            internal_transaction_categories
        )
        df = self._dataframe_cache[~mask]
        return df

    def _get_internal_transactions(self):
        internal_transaction_categories = (
            self._config.get_internal_transaction_categories()
        )
        mask = self._dataframe_cache[DataColumns.CATEGORY].isin(
            internal_transaction_categories
        )
        df = self._dataframe_cache[mask]
        return df

    def plot_pie_chart_per_cateogry(self):

        if not self.dataset_is_valid():
            return go.Figure()

        amount_per_category = self._get_abs_payment_amount_per_category()
        total_months = self._total_months_in_dataset()

        average_payment_per_month = [v / total_months for v in amount_per_category]

        fig = go.Figure()
        fig.add_trace(
            go.Pie(
                values=amount_per_category,
                labels=amount_per_category.index,
                text=average_payment_per_month,
                textinfo="percent",
                hovertemplate=f"%{{label}} (%{{percent}})<br>"
                f"∅ %{{text:.2f}} {CURRENCY_SYMBOL}/Month<br>"
                f"Total: %{{value:.2f}} {CURRENCY_SYMBOL}<extra></extra>",
            )
        )
        fig.update_traces(
            marker=dict(
                colors=[
                    self.category_to_color_map[c] for c in amount_per_category.index
                ]
            )
        )
        fig.update_layout(title="Payments per Category")
        return fig

    def _total_months_in_dataset(self):
        total_time_delta = relativedelta.relativedelta(
            self._dataframe_cache.index.max().date(),
            self._dataframe_cache.index.min().date(),
        )
        total_months = (
            total_time_delta.years * 12
            + total_time_delta.months
            + (1 if total_time_delta.days > 15 else 0)
        )
        return total_months

    def _get_abs_payment_amount_per_category(self):
        grouped_per_category = self._dataframe_cache[
            self._dataframe_cache[DataColumns.AMOUNT] < 0
        ].groupby(by=DataColumns.CATEGORY)
        amount_per_category = grouped_per_category[DataColumns.AMOUNT].sum().abs()
        return amount_per_category

    def plot_cateogory_variance(self):
        if not self.dataset_is_valid():
            return go.Figure()

        fig = go.Figure()

        df = (
            self._dataframe_cache.groupby(["date_without_day", DataColumns.CATEGORY])
            .sum()
            .reset_index()
        )

        for category in df[DataColumns.CATEGORY].unique():

            mask = df[DataColumns.CATEGORY] == category
            curr_df = df[mask]

            fig.add_trace(
                go.Box(
                    name=category,
                    y=curr_df[DataColumns.AMOUNT],
                    marker_color=self.category_to_color_map[category],
                ),
            )

        fig.update_layout(
            title="Variance per Cateogry per Month",
            xaxis_title="Categories",
            yaxis_title=f"Distribution per Month [{CURRENCY_SYMBOL}]",
            showlegend=True,
        )
        return fig
