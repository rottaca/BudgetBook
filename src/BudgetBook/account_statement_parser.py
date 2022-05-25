from datetime import datetime
import numpy as np
import pandas as pd
import Levenshtein
from sklearn.cluster import dbscan
from plotly import graph_objects as go

from BudgetBook.category_parser import CategoryParser
from BudgetBook.config_parser import DataColumns, ConfigParser
from BudgetBook.dated_transaction import DatedTransaction


class AccountStatementCsvParser:
    def __init__(self, csv_statement_path_or_iostream, config):
        self._config = config
        self._category_parser = CategoryParser(self._config)

        map_internal_to_csv_column = self._config.get_csv_columns_mapping()
        map_csv_to_internal_column = {
            v: k for k, v in map_internal_to_csv_column.items()
        }

        self._csv_data = pd.read_csv(
            csv_statement_path_or_iostream,
            sep=";",
            decimal=",",
            na_filter=False,
            dtype={
                map_internal_to_csv_column[DataColumns.AMOUNT]: np.float32,
                map_internal_to_csv_column[DataColumns.DESCRIPTION]: str,
                map_internal_to_csv_column[DataColumns.PAYMENT_PARTY]: str,
                map_internal_to_csv_column[DataColumns.TYPE_OF_TRANSFER]: str,
                map_internal_to_csv_column[DataColumns.DATE]: str,
            },
        )

        # Rename columns to internal names
        self._csv_data = self._csv_data[map_internal_to_csv_column.values()]
        self._csv_data.rename(
            columns=map_csv_to_internal_column,
            inplace=True,
        )

        # Parse date
        self._csv_data[DataColumns.DATE] = pd.to_datetime(
            self._csv_data[DataColumns.DATE], format=self._config.get_csv_date_format()
        )

    def to_dated_transactions(self):
        self.to_regular_transactions()

        scheduled_transactions = []
        for _, row in self._csv_data.iterrows():
            scheduled_transactions.append(
                DatedTransaction(
                    row[DataColumns.PAYMENT_PARTY],
                    row[DataColumns.DATE].date(),
                    row[DataColumns.AMOUNT],
                    row[DataColumns.DESCRIPTION],
                    self._category_parser.get_category_for_record(row),
                )
            )

        return scheduled_transactions

    def to_regular_transactions(self):

        distances = []

        payment_partys = self._csv_data[DataColumns.PAYMENT_PARTY].unique()

        same_party_label = AccountStatementCsvParser.group_by_similarity(
            payment_partys, eps=3
        )

        grouped_payment_parties = [
            payment_partys[same_party_label == l].tolist()
            for l in np.unique(same_party_label)
            if l >= 0
        ]
        grouped_payment_parties.extend(
            [p] for p in payment_partys[same_party_label == -1]
        )

        grouped_data = {}

        for curr_payment_partys in grouped_payment_parties:
            df_same_group = self._csv_data[
                self._csv_data[DataColumns.PAYMENT_PARTY].isin(curr_payment_partys)
            ]

            print("Payment parties:", curr_payment_partys)
            grouped_data[tuple(curr_payment_partys)] = []

            desc = df_same_group[DataColumns.DESCRIPTION]

            labels = AccountStatementCsvParser.group_by_similarity(
                [d[:40] for d in desc], eps=5
            )
            for l in pd.Series(labels).unique():
                data_per_group = df_same_group[labels == l][
                    [DataColumns.AMOUNT, DataColumns.DATE, DataColumns.DESCRIPTION]
                ]

                if l == -1:
                    print("No cluster")
                    grouped_data[tuple(curr_payment_partys)].extend(
                        [[d] for d in data_per_group]
                    )
                else:
                    print("Label", l)
                    grouped_data[tuple(curr_payment_partys)].append(data_per_group)

                print(data_per_group)

    @staticmethod
    def gen_lev_distance_for(series: pd.Series):
        def lev_metric(x, y):
            i, j = int(x[0]), int(y[0])  # extract indices
            if isinstance(series, pd.Series):
                return Levenshtein.distance(series.iloc[i], series.iloc[j])
            else:
                return Levenshtein.distance(series[i], series[j])

        return lev_metric

    @staticmethod
    def group_by_similarity(data_series, eps):
        X = np.arange(len(data_series)).reshape(-1, 1)
        _, labels = dbscan(
            X,
            metric=AccountStatementCsvParser.gen_lev_distance_for(data_series),
            eps=eps,
            min_samples=2,
        )

        return labels
