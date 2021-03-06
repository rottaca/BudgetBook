import numpy as np
import pandas as pd

from BudgetBook.category_parser import CategoryParser
from BudgetBook.config_parser import DataColumns
from BudgetBook.dated_transaction import DatedTransaction


class AccountStatementCsvParser:
    def __init__(self, csv_statement_path_or_iostream_or_dataframe, config):
        self._config = config
        self._category_parser = CategoryParser(self._config)

        map_internal_to_csv_column = self._config.get_csv_columns_mapping()
        map_csv_to_internal_column = {
            v: k for k, v in map_internal_to_csv_column.items()
        }

        if isinstance(csv_statement_path_or_iostream_or_dataframe, pd.DataFrame):
            self._csv_data = csv_statement_path_or_iostream_or_dataframe
        else:
            self._csv_data = pd.read_csv(
                csv_statement_path_or_iostream_or_dataframe,
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
                self._csv_data[DataColumns.DATE],
                format=self._config.get_csv_date_format(),
            )

    def get_csv_dataframe(self):
        return self._csv_data

    def to_dated_transactions(self):
        transactions = []
        for _, row in self._csv_data.iterrows():
            transactions.append(
                DatedTransaction(
                    row[DataColumns.PAYMENT_PARTY],
                    row[DataColumns.DATE].date(),
                    row[DataColumns.AMOUNT],
                    row[DataColumns.DESCRIPTION],
                    self._category_parser.get_category_for_record(row),
                )
            )

        return transactions
