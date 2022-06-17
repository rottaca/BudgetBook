import enum
import yaml

from BudgetBook.helper import CURRENCY_SYMBOL


class ConfigKeywords:
    CATGORY_MAPPING_TOPLEVEL = "category_mapping"

    CATEGORY_RULE_AND = "and"
    CATEGORY_RULE_OR = "or"

    CSV_STATEMENT_PARSER_TOPLEVEL = "statement_parser"
    CSV_COLUMNS_TOPLEVEL = "csv_columns"

    CSV_DATE_FORMAT = "date_format"

    CATEGORIES_TO_IGNORE = "internal_transfer_categories"


class DataColumns:
    PAYMENT_PARTY = "payment_party"
    AMOUNT = "amount"
    TYPE_OF_TRANSFER = "type_of_transfer"
    DESCRIPTION = "description"
    DATE = "date"
    CATEGORY = "category"


DATA_COLUMN_TO_DISPLAY_NAME = {
    DataColumns.PAYMENT_PARTY: "Payment Party",
    DataColumns.AMOUNT: f"Amount [{CURRENCY_SYMBOL}]",
    DataColumns.TYPE_OF_TRANSFER: "Type Of Transfer",
    DataColumns.DESCRIPTION: "Description",
    DataColumns.DATE: "Date",
    DataColumns.CATEGORY: "Category",
}


class Config:
    __shared_state = None

    def __init__(self, yaml_file_path: str=None) -> None:
        if yaml_file_path is not None:
            with open(yaml_file_path, "r") as stream:
                self._config = yaml.safe_load(stream)

            self._category_mapping = self._config[ConfigKeywords.CATGORY_MAPPING_TOPLEVEL]
            self._statement_parser = self._config[
                ConfigKeywords.CSV_STATEMENT_PARSER_TOPLEVEL
            ]
            self._csv_statement_columns = self._statement_parser[
                ConfigKeywords.CSV_COLUMNS_TOPLEVEL
            ]
            Config.__shared_state = self.__dict__
        elif Config.__shared_state is not None:
            self.__dict__ = Config.__shared_state 
        else:
            raise AttributeError("No config created yet!")


    def get_internal_transaction_categories(self) -> list:
        return self._statement_parser[ConfigKeywords.CATEGORIES_TO_IGNORE]

    def get_csv_date_format(self) -> str:
        return self._statement_parser[ConfigKeywords.CSV_DATE_FORMAT]

    def get_category_mapping(self) -> dict:
        return self._category_mapping

    def get_csv_columns_mapping(self) -> dict:
        return self._csv_statement_columns
