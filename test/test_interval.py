from datetime import date
from pprint import pprint
import random
import sys, os.path
import pandas as pd
import plotly
import plotly.express as px

pd.options.plotting.backend = "plotly"

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(SRC_DIR)

from BudgetBook.transaction_visualizer import TransactionVisualizer
from BudgetBook.dated_transaction import DatedTransaction
from BudgetBook.helper import Category
from BudgetBook.transaction_interval import TransactionInterval
from BudgetBook.regular_event import RegularEvent
from BudgetBook.regular_transaction import RegularTransaction
from BudgetBook.regular_transaction_builder import RegularTransactionBuilder


def year(year: int) -> date:
    return date(year=year, month=1, day=1)


def test_interval_iteration():
    interval = RegularEvent(
        first_occurence=year(2022), interval_size=TransactionInterval.monthly()
    )

    generated_intervals = [
        i for i in interval.iterate(from_date=year(2022), up_to=year(2023))
    ]
    expected_intervals = [date(year=2022, month=i, day=1) for i in range(1, 13)]
    # pprint(generated_intervals)
    # pprint(expected_intervals)
    assert all(
        expected == actual
        for expected, actual in zip(expected_intervals, generated_intervals)
    )


def test_regular_transaction():
    Regular_payment = RegularTransaction(
        "MyPayment",
        Category.UNKNOWN_PAYMENT,
        100.0,
        RegularEvent(
            first_occurence=year(2022), interval_size=TransactionInterval.monthly()
        ),
        "no desc",
    )

    generated_payments = [
        p
        for p in Regular_payment.iterate(
            from_date=year(2022), up_to=date(year=2023, month=5, day=1)
        )
    ]
    expected_intervals = [
        DatedTransaction(
            "test",
            "no desc",
            Category.UNKNOWN_PAYMENT,
            date(year=2022, month=i, day=1),
            100.0,
        )
        for i in range(1, 13)
    ]
    expected_intervals.extend(
        [
            DatedTransaction(
                "test",
                "no desc",
                Category.UNKNOWN_PAYMENT,
                date(year=2023, month=i, day=1),
                100.0,
            )
            for i in range(1, 5)
        ]
    )

    assert all(
        (expected.get_date() == actual.get_date())
        and (expected.get_amount() == actual.get_amount())
        for expected, actual in zip(expected_intervals, generated_payments)
    )


def test_Regular_payment_builder():
    builder = RegularTransactionBuilder()
    builder.set_first_ocurrence(2022)
    builder.set_last_ocurrence(2023)
    builder.set_interval_monthly()
    builder.set_category(Category.UNKNOWN_PAYMENT)
    builder.build_regular_transaction("MyPayment1", -100.0)
    builder.set_interval(months=2)
    builder.set_category(Category.SALERY)
    builder.build_regular_transaction("MySalery", 1000.0)

    scheduled_transactions = builder.get_scheduled_transactions()

    assert len(scheduled_transactions) == 2
    assert scheduled_transactions[0].amount == -100.0
    assert scheduled_transactions[0].name == "MyPayment1"
    assert scheduled_transactions[1].amount == 1000.0
    assert scheduled_transactions[1].name == "MySalery"


def test_bank_transaction_visualizer():
    builder = RegularTransactionBuilder()
    builder.set_first_ocurrence(2022)
    builder.set_last_ocurrence(2023)
    builder.set_interval_monthly()
    builder.set_category(Category.UNKNOWN_PAYMENT)
    builder.build_regular_transaction("MyPayment1", -100.0)
    builder.set_interval(months=2)
    builder.set_category(Category.SALERY)
    builder.build_regular_transaction("MySalery", 1000.0)

    scheduled_transactions = builder.get_scheduled_transactions()

    visualzier = TransactionVisualizer()
    visualzier.add_transactions(scheduled_transactions)

    visualzier.set_analysis_interval(from_date=year(2022), to_date=year(2023))


def test_random_data_plots():

    builder = RegularTransactionBuilder()
    builder.set_first_ocurrence(2022)
    builder.set_last_ocurrence(2023)
    for i in range(10):
        amount = (random.random() - 0.5) * 1000.0
        cat = (
            Category.SALERY
            if amount > 0
            else Category(random.randint(1, len(Category) - 1))
        )
        builder.set_category(cat)
        builder.set_interval(0, random.randint(1, 5), 0)
        builder.build_regular_transaction(f"dummy {i}", amount)

    scheduled_transactions = builder.get_scheduled_transactions()

    manager = TransactionVisualizer()
    manager.add_transactions(scheduled_transactions)
    manager.set_analysis_interval(year(2022), year(2023))

    df = manager._to_dataframe()
    print(df)
