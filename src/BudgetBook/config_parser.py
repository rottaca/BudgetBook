import enum
import yaml


@enum.unique
class ConfigKeywords(enum.Enum):
    CATGORY_MAPPING_TOPLEVEL = "category_mapping"

    CATEGORY_RULE_AND = "and"
    CATEGORY_RULE_OR = "or"
    CATEGORY_RULE_DESC_FILTER = "desc"
    CATEGORY_RULE_SENDER_FILTER = "sender"

    CSV_STATEMENT_PARSER_TOPLEVEL = "statement_parser"
    CSV_COLUMNS_TOPLEVEL = "csv_columns"
    CSV_COL_PAYMENT_PARTY = "payment_party"
    CSV_COL_AMOUNT = "amount"
    CSV_COL_TYPE_OF_TRANSFER = "type_of_transfer"
    CSV_COL_DESCRIPTION = "description"
    CSV_COL_DATE = "date"

    CSV_DATE_FORMAT = "date_format"


class ConfigParser:
    def __init__(self, yaml_file_path: str) -> None:
        with open(yaml_file_path, "r") as stream:
            self._config = yaml.safe_load(stream)

        self._category_mapping = self._config[
            ConfigKeywords.CATGORY_MAPPING_TOPLEVEL.value
        ]
        self._statement_parser = self._config[
            ConfigKeywords.CSV_STATEMENT_PARSER_TOPLEVEL.value
        ]
        self._csv_statement_columns = self._statement_parser[
            ConfigKeywords.CSV_COLUMNS_TOPLEVEL.value
        ]

    def get_category_mapping(self):
        return self._category_mapping

    def get_csv_column_payment_party(self):
        return self._csv_statement_columns[ConfigKeywords.CSV_COL_PAYMENT_PARTY.value]

    def get_csv_column_amount(self):
        return self._csv_statement_columns[ConfigKeywords.CSV_COL_AMOUNT.value]

    def get_csv_column_type_of_transfer(self):
        return self._csv_statement_columns[
            ConfigKeywords.CSV_COL_TYPE_OF_TRANSFER.value
        ]

    def get_csv_column_description(self):
        return self._csv_statement_columns[ConfigKeywords.CSV_COL_DESCRIPTION.value]

    def get_csv_column_date(self):
        return self._csv_statement_columns[ConfigKeywords.CSV_COL_DATE.value]

    def get_csv_date_format(self):
        return self._statement_parser[ConfigKeywords.CSV_DATE_FORMAT.value]
