
from datetime import date
from dateutil.relativedelta import relativedelta

import os
import sys

import pytest

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(SRC_DIR)

from BudgetBook.regular_event import RegularEvent
from BudgetBook.transaction_interval import TransactionInterval

def test_regular_event_getters():
    event = RegularEvent(
        first_occurence=date(2022, 5, 23),
        interval_size=TransactionInterval(days=10),
        last_occurence=date(2023, 7, 11)
    )

    assert event.get_first_occurence() == date(2022, 5, 23)
    assert event.get_last_occurence() == date(2023, 7, 11)
    assert event.get_interval_size() == relativedelta(days=10)
    
def test_regular_event_iteration():
    event = RegularEvent(
        first_occurence=date(2022, 5, 23),
        interval_size=TransactionInterval(days=22),
        last_occurence=date(2023, 7, 11)
    )
    
    itr = event.iterate(from_date=date(2022, 1, 1), up_to=date(2022,12,30))

    assert next(itr) == date(2022, 5, 23)
    assert next(itr) == date(2022, 6, 14)
    assert next(itr) == date(2022, 7, 6)
    assert next(itr) == date(2022, 7, 28)
    assert next(itr) == date(2022, 8, 19)
    assert next(itr) == date(2022, 9, 10)
    assert next(itr) == date(2022, 10, 2)
    assert next(itr) == date(2022, 10, 24)
    assert next(itr) == date(2022, 11, 15)
    assert next(itr) == date(2022, 12, 7)
    assert next(itr) == date(2022, 12, 29)

    with pytest.raises(StopIteration) as e_info:
        assert next(itr) == None


def test_regular_event_monthly():
    event = RegularEvent(
        first_occurence=date(2022, 1, 1),
        interval_size=TransactionInterval.monthly(),
    )

    num_events = sum([1 for i in event.iterate(from_date=date(2022,1,1), up_to=date(2023,1,1))])

    assert num_events == 12
