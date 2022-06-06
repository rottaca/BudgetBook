from BudgetBook.transaction_interval import TransactionInterval

import os
import sys

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(SRC_DIR)

def test_interval():

    interval = TransactionInterval(days=1)

    relative = interval
    assert relative.days == 1
    assert relative.months == 0
    assert relative.years == 0