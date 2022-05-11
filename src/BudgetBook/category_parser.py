import enum
import yaml

from BudgetBook.config_parser import ConfigKeywords, ConfigParser


class CategoryParser:
    def __init__(self, config: ConfigParser) -> None:
        self._config = config
        self._category_mapping = config.get_category_mapping()
        self._csv_columns_mapping = config.get_csv_columns_mapping()

    def get_category_for_record(self, record):
        for category, mapping_rules in self._category_mapping.items():
            if self._check_category_match(record, mapping_rules):
                return category

        return (
            "UNKNOWN_INCOME"
            if record[self._csv_columns_mapping[ConfigKeywords.CSV_COL_AMOUNT.value]]
            > 0
            else "UNKNOWN_PAYMENT"
        )

    @staticmethod
    def _field_contains_any(field, candiates):
        return any(v.lower() in field.lower() for v in candiates)

    def _check_and(self, record, mapping_rules):
        for filter_key, filter_values in mapping_rules[
            ConfigKeywords.CATEGORY_RULE_AND.value
        ].items():
            if not self._check_category_match(
                record,
                {filter_key: filter_values},
            ):
                return False
        return True

    def _check_or(self, record, mapping_rules):
        for filter_key, filter_values in mapping_rules[
            ConfigKeywords.CATEGORY_RULE_OR.value
        ].items():
            if self._check_category_match(
                record,
                {filter_key: filter_values},
            ):
                return True
        return False

    def _check_category_match(self, record, mapping_rules):
        has_and = ConfigKeywords.CATEGORY_RULE_AND.value in mapping_rules
        has_or = ConfigKeywords.CATEGORY_RULE_OR.value in mapping_rules

        if has_and:
            return self._check_and(record, mapping_rules)
        elif has_or:
            return self._check_or(record, mapping_rules)
        else:
            for filter_key, filter_values in mapping_rules.items():
                if CategoryParser._field_contains_any(
                    record[self._csv_columns_mapping[filter_key]], filter_values
                ):
                    return True

        return False
