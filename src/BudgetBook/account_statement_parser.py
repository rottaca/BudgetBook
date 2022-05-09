import pandas as pd

from BudgetBook.category_parser import CategoryParser
from BudgetBook.regular_event import RegularEvent
from BudgetBook.regular_money_transfer import RegularMoneyTransfer


class AccountStatementCsvParser:
    def __init__(self, csv_path, category_mapping_path):
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

        self._csv_data[self._col_name_sender_receiver] = (
            self._csv_data[self._col_name_sender_receiver]
            .astype(str)
            .apply(lambda x: x.replace("nan", "Unknown"))
        )

        self._csv_data[self._col_transfer_desc] = self._csv_data[
            self._col_transfer_desc
        ].astype(str)

        self._csv_data[self._col_date] = pd.to_datetime(
            self._csv_data[self._col_date], format=self._col_date_format
        )
        self._category_parser = CategoryParser(category_mapping_path)

        self._preprocess()

    def _preprocess(self):
        self._unique_sender_receiver = self._csv_data[
            self._col_name_sender_receiver
        ].unique()

        self._unique_transfer_types = self._csv_data[self._col_type_of_transer].unique()

    def to_scheduled_transfers(self):
        scheduled_transfers = []
        for _, row in self._csv_data.iterrows():
            scheduled_transfers.append(
                RegularMoneyTransfer(
                    row[self._col_name_sender_receiver],
                    self._map_to_category(row),
                    row[self._col_amount],
                    RegularEvent.once(row[self._col_date].date()),
                )
            )

        print("done scheduling")

        return scheduled_transfers

    def _map_to_category(self, row):
        return self._category_parser.get_category(
            row[self._col_amount],
            row[self._col_name_sender_receiver],
            row[self._col_transfer_desc],
        )
