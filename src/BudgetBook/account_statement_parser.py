import pandas as pd

from BudgetBook.category_parser import CategoryParser
from BudgetBook.config_parser import ConfigParser
from BudgetBook.dated_bank_transfer import DatedBankTransfer


class AccountStatementCsvParser:
    def __init__(self, csv_statement_path, config_path):
        self._config = ConfigParser(config_path)
        self._category_parser = CategoryParser(self._config)

        self._col_name_sender_receiver = self._config.get_csv_column_payment_party()
        self._col_amount = "Betrag"
        self._col_type_of_transer = "Buchungstext"
        self._col_transfer_desc = "Verwendungszweck"
        self._col_date = "Buchungstag"
        self._col_date_format = "%d.%m.%Y"

        self._csv_data = pd.read_csv(csv_statement_path, sep=";")
        self._csv_data[self._col_amount] = (
            self._csv_data[self._col_amount]
            .apply(lambda x: x.replace(",", "."))
            .astype(float)
        )

        self._csv_data[self._col_name_sender_receiver] = (
            self._csv_data[self._col_name_sender_receiver]
            .astype(str)
            .apply(lambda x: x.replace("nan", "Unknown"))
        )

        self._csv_data[self._col_transfer_desc] = self._csv_data[
            self._col_transfer_desc
        ].astype(str)

        self._csv_data[self._col_date] = pd.to_datetime(
            self._csv_data[self._col_date], format=self._config.get_csv_date_format()
        )

    def to_scheduled_transfers(self):
        scheduled_transfers = []
        for _, row in self._csv_data.iterrows():
            scheduled_transfers.append(
                DatedBankTransfer(
                    self._get_payment_party(row),
                    self._get_date(row),
                    self._get_amount(row),
                    self._get_description(row),
                    self._category_parser.get_category_for_record(row),
                )
            )

        return scheduled_transfers

    def _get_amount(self, df):
        return df[self._config.get_csv_column_amount()]

    def _get_payment_party(self, df):
        return df[self._config.get_csv_column_payment_party()]

    def _get_type_of_transfer(self, df):
        return df[self._config.get_csv_column_type_of_transfer()]

    def _get_description(self, df):
        return df[self._config.get_csv_column_description()]

    def _get_date(self, df):
        return df[self._config.get_csv_column_date()].date()
