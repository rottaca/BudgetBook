from datetime import date
import os
import sys

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(SRC_DIR)

from BudgetBook.config_parser import DataColumns
from BudgetBook.dated_transaction import DatedTransaction


def test_creation():
    d = DatedTransaction(
        "PaymentParty",
        date(2022, 5, 23),
        100.0,
        "My Description",
        "My Category"
    )

    dct = d.to_dict()
    assert dct[DataColumns.PAYMENT_PARTY] == "PaymentParty"
    assert dct[DataColumns.DATE] == date(2022, 5, 23)
    assert dct[DataColumns.AMOUNT] == 100.0
    assert dct[DataColumns.DESCRIPTION] == "My Description"
    assert dct[DataColumns.CATEGORY] == "My Category"