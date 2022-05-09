import yaml


class CategoryParser:
    def __init__(self, yaml_file_path: str) -> None:
        with open(yaml_file_path, "r") as stream:
            self._category_mapping = yaml.safe_load(stream)["category_mapping"]

    def get_category(self, amount, name_sender, description):
        description = description.lower()
        name_sender = name_sender.lower()

        for category, mapping_rules in self._category_mapping.items():
            if self._check_category_match(name_sender, description, mapping_rules):
                return category

        return "UNKNOWN_INCOME" if amount > 0 else "UNKNOWN_PAYMENT"

    @staticmethod
    def _field_contains_any(field, candiates):
        return any(v.lower() in field for v in candiates)

    @staticmethod
    def _check_description(description, mapping_rules):
        if CategoryParser._field_contains_any(description, mapping_rules["desc"]):
            return True
        else:
            return False

    @staticmethod
    def _check_sender(name_sender, mapping_rules):
        if CategoryParser._field_contains_any(name_sender, mapping_rules["sender"]):
            return True
        else:
            return False

    def _check_category_match(self, name_sender, description, mapping_rules):
        has_and = "and" in mapping_rules
        has_or = "or" in mapping_rules
        has_description = "desc" in mapping_rules
        has_sender = "sender" in mapping_rules

        if has_description and CategoryParser._check_description(
            description, mapping_rules
        ):
            return True

        if has_sender and CategoryParser._check_sender(name_sender, mapping_rules):
            return True

        if has_and:
            for m in mapping_rules["and"]:
                if not self._check_category_match(
                    name_sender, description, {m: mapping_rules["and"][m]}
                ):
                    return False
        if has_or:
            for m in mapping_rules["or"]:
                if self._check_category_match(
                    name_sender, description, {m: mapping_rules["or"][m]}
                ):
                    return True

        return False
