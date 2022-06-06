
from datetime import date
from dateutil.relativedelta import relativedelta

import os
import sys

import pytest
from BudgetBook.dated_transaction import DatedTransaction

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(SRC_DIR)

from BudgetBook.regular_event import RegularEvent
from BudgetBook.config_parser import DataColumns
from BudgetBook.transaction_interval import TransactionInterval
from BudgetBook.regular_transaction import RegularTransaction

def test_regular_transaction_getters():
    
    frequency = RegularEvent(
        first_occurence=date(2022, 1, 1),
        interval_size=TransactionInterval.monthly(),
        last_occurence=date(2023, 1,1)
    )

    regular_transaction = RegularTransaction(
        "Payment Party",
        frequency,
        100.0,
        "My Desc",
        "My Category"
    )

    assert regular_transaction.get_frequency().get_first_occurence() == date(2022, 1, 1)
    assert regular_transaction.get_frequency().get_last_occurence() == date(2023, 1, 1)
    assert regular_transaction.get_frequency().get_interval_size() == relativedelta(months=1)
    
    dct = regular_transaction.to_dict()
    assert dct[DataColumns.PAYMENT_PARTY] == "Payment Party"
    assert dct["Frequency"] == 'every 1 months from 2022-01-01 to 2023-01-01' 
    assert dct[DataColumns.AMOUNT] == 100.0
    assert dct[DataColumns.DESCRIPTION] == "My Desc"
    assert dct[DataColumns.CATEGORY] == "My Category"

    
def test_regular_transaction_iteration():
    
    frequency = RegularEvent(
        first_occurence=date(2022, 1, 1),
        interval_size=TransactionInterval.monthly(),
        last_occurence=date(2023, 1,1)
    )

    regular_transaction = RegularTransaction(
        "Payment Party",
        frequency,
        100.0,
        "My Desc",
        "My Category"
    )
    
    itr = regular_transaction.iterate(from_date=date(2022, 1, 1), up_to=date(2023,1,1))

    dated_transaction: DatedTransaction = next(itr)
    
    assert dated_transaction.date == date(2022, 1,1)
    assert dated_transaction.amount == 100.0
    assert dated_transaction.category == "My Category"
    assert dated_transaction.desc == "My Desc"
    assert dated_transaction.payment_party == "Payment Party"

    amount_sum = 100.0 + sum([t.amount for t in itr])
    assert amount_sum == 1200.0
