import enum
import yaml

from BudgetBook.config_parser import ConfigKeywords


class CategoryParser:
    def __init__(self, category_mapping: str) -> None:
        self._category_mapping = category_mapping

    def get_category(self, amount, payment_party, description):
        description = description.lower()
        payment_party = payment_party.lower()

        for category, mapping_rules in self._category_mapping.items():
            if self._check_category_match(payment_party, description, mapping_rules):
                return category

        return "UNKNOWN_INCOME" if amount > 0 else "UNKNOWN_PAYMENT"

    @staticmethod
    def _field_contains_any(field, candiates):
        return any(v.lower() in field for v in candiates)

    @staticmethod
    def _check_description(description, mapping_rules):
        return CategoryParser._field_contains_any(
            description, mapping_rules[ConfigKeywords.CATEGORY_RULE_DESC_FILTER.value]
        )

    @staticmethod
    def _check_sender(payment_party, mapping_rules):
        return CategoryParser._field_contains_any(
            payment_party,
            mapping_rules[ConfigKeywords.CATEGORY_RULE_SENDER_FILTER.value],
        )

    def _check_and(
        self,
        mapping_rules,
        payment_party,
        description,
    ):
        for filter_key, filter_values in mapping_rules[
            ConfigKeywords.CATEGORY_RULE_AND.value
        ].items():
            if not self._check_category_match(
                payment_party,
                description,
                {filter_key: filter_values},
            ):
                return False
        return True

    def _check_or(
        self,
        mapping_rules,
        payment_party,
        description,
    ):
        for filter_key, filter_values in mapping_rules[
            ConfigKeywords.CATEGORY_RULE_OR.value
        ].items():
            if self._check_category_match(
                payment_party,
                description,
                {filter_key: filter_values},
            ):
                return True
        return False

    def _check_category_match(self, payment_party, description, mapping_rules):
        has_and = ConfigKeywords.CATEGORY_RULE_AND.value in mapping_rules
        has_or = ConfigKeywords.CATEGORY_RULE_OR.value in mapping_rules
        has_description = (
            ConfigKeywords.CATEGORY_RULE_DESC_FILTER.value in mapping_rules
        )
        has_sender = ConfigKeywords.CATEGORY_RULE_SENDER_FILTER.value in mapping_rules

        if has_description and CategoryParser._check_description(
            description, mapping_rules
        ):
            return True

        if has_sender and CategoryParser._check_sender(payment_party, mapping_rules):
            return True

        if has_and:
            return self._check_and(
                mapping_rules,
                payment_party,
                description,
            )
        if has_or:
            return self._check_or(
                mapping_rules,
                payment_party,
                description,
            )

        return False
