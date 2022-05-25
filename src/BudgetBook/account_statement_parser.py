from datetime import datetime
import numpy as np
import pandas as pd
from plotly import graph_objects as go

from BudgetBook.category_parser import CategoryParser
from BudgetBook.config_parser import DataColumns, ConfigParser
from BudgetBook.dated_bank_transfer import DatedBankTransfer


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

    def to_dated_bank_transfers(self):
        self.to_regular_bank_transfers()
        scheduled_transfers = []
        for _, row in self._csv_data.iterrows():
            scheduled_transfers.append(
                DatedBankTransfer(
                    row[DataColumns.PAYMENT_PARTY],
                    row[DataColumns.DATE].date(),
                    row[DataColumns.AMOUNT],
                    row[DataColumns.DESCRIPTION],
                    self._category_parser.get_category_for_record(row),
                )
            )

        return scheduled_transfers

    
    def to_regular_bank_transfers(self):
        import Levenshtein 
        from sklearn.cluster import dbscan
        distances = []

        payment_partys = self._csv_data[DataColumns.PAYMENT_PARTY].unique()
        def lev_metric(x, y):
            i, j = int(x[0]), int(y[0])     # extract indices
            return Levenshtein.distance(payment_partys[i], payment_partys[j])

        X = np.arange(len(payment_partys)).reshape(-1, 1)
        _, same_party_label = dbscan(X, metric=lev_metric, eps=3, min_samples=2)

        grouped_payment_parties = [payment_partys[same_party_label==l].tolist() for l in np.unique(same_party_label) if l >= 0]
        grouped_payment_parties.extend([p] for p in payment_partys[same_party_label==-1])

        for curr_payment_partys in grouped_payment_parties:
            df_same_group = self._csv_data[self._csv_data[DataColumns.PAYMENT_PARTY].isin(curr_payment_partys)]
            
            print("Payment parties:", curr_payment_partys)

            desc = df_same_group[DataColumns.DESCRIPTION]
            def lev_metric(x, y):
                i, j = int(x[0]), int(y[0])     # extract indices
                return Levenshtein.distance(desc.iloc[i], desc.iloc[j])

            X = np.arange(len(desc)).reshape(-1, 1)
            _, labels = dbscan(X, metric=lev_metric, eps=35, min_samples=2)
            for l in pd.Series(labels).unique():
                if l == -1:
                    print("No cluster")
                else:
                    print("Label", l)
                print(df_same_group[labels == l][[DataColumns.AMOUNT, DataColumns.DATE, DataColumns.DESCRIPTION]])

            

            


