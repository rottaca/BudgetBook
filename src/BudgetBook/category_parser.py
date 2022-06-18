from BudgetBook.config_parser import DATA_COLUMN_TO_DISPLAY_NAME, DataColumns, ConfigKeywords, Config


class InvalidCateogryMappingException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class CategoryParser:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._category_mapping = config.get_category_mapping()
        self._csv_columns_mapping = config.get_csv_columns_mapping()

        self._validate_category_mapping()


    def _validate_category_mapping(self):
        for category, rules in self._category_mapping.items():
            for rule_name, rule_value in rules.items():
                valid_rule_names = [ConfigKeywords.CATEGORY_RULE_AND, ConfigKeywords.CATEGORY_RULE_OR, *DATA_COLUMN_TO_DISPLAY_NAME.keys()]
                if rule_name not in valid_rule_names:
                    raise InvalidCateogryMappingException(f"Provided rule name '{rule_name}' not allowed. Use one of: '{valid_rule_names}'.")

                if type(rule_value) not in [list, dict]:
                    raise InvalidCateogryMappingException(f"Provided rule value '{rule_value}' for rule '{rule_name}' not allowed. Use one of: 'list, dict'.")            
        
    def get_parent_category_for_child(self, child_category_name: str):
        try:
            return self._category_mapping[child_category_name][ConfigKeywords.CATEGORY_PARENT]
        except KeyError:
            return ""

    def get_category_for_record(self, record):
        if DataColumns.CATEGORY in record:
            return record[DataColumns.CATEGORY]

        for category, rules in self._category_mapping.items():
            if self._check_category_match(record, rules):
                return category

        return ConfigKeywords.CATEGORY_DEFAULT_UNKNOWN_INCOME if record[DataColumns.AMOUNT] > 0 else ConfigKeywords.CATEGORY_DEFAULT_UNKNOWN_PAYMENT

    @staticmethod
    def _check_category_match(record, mapping_rules):
        has_and = ConfigKeywords.CATEGORY_RULE_AND in mapping_rules
        has_or = ConfigKeywords.CATEGORY_RULE_OR in mapping_rules

        if has_and:
            return CategoryParser._check_and(record, mapping_rules)
        elif has_or:
            return CategoryParser._check_or(record, mapping_rules)
        else:
            for filter_key, filter_values in mapping_rules.items():
                if CategoryParser._field_contains_any(
                    record[filter_key], filter_values
                ):
                    return True

        return False

    @staticmethod
    def _field_contains_any(field, candiates):
        return any(v.lower() in field.lower() for v in candiates)

    @staticmethod
    def _check_and(record, mapping_rules):
        for filter_key, filter_values in mapping_rules[
            ConfigKeywords.CATEGORY_RULE_AND
        ].items():
            if not CategoryParser._check_category_match(
                record,
                {filter_key: filter_values},
            ):
                return False
        return True

    @staticmethod
    def _check_or(record, mapping_rules):
        for filter_key, filter_values in mapping_rules[
            ConfigKeywords.CATEGORY_RULE_OR
        ].items():
            if CategoryParser._check_category_match(
                record,
                {filter_key: filter_values},
            ):
                return True
        return False
