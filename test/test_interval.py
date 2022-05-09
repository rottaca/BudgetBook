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

from BudgetBook.money_transfer_visualizer import (
    Category,
    DatedMoneyTransfer,
    MoneyTransferVisualizer,
    ReocurringEvent,
    MoneyTransferInterval,
    ReocurringMoneyTransfer,
    ReocurringMoneyTransferBuilder,
)


def year(year: int) -> date:
    return date(year=year, month=1, day=1)


def test_interval_iteration():
    interval = ReocurringEvent(
        first_occurence=year(2022), interval_size=MoneyTransferInterval.monthly()
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


def test_reocurring_transfer():
    reocurring_payment = ReocurringMoneyTransfer(
        "MyPayment",
        Category.UNKNOWN,
        100.0,
        ReocurringEvent(
            first_occurence=year(2022), interval_size=MoneyTransferInterval.monthly()
        ),
    )

    generated_payments = [
        p
        for p in reocurring_payment.iterate(
            from_date=year(2022), up_to=date(year=2023, month=5, day=1)
        )
    ]
    expected_intervals = [
        DatedMoneyTransfer("test", date(year=2022, month=i, day=1), 100.0)
        for i in range(1, 13)
    ]
    expected_intervals.extend(
        [
            DatedMoneyTransfer("test", date(year=2023, month=i, day=1), 100.0)
            for i in range(1, 5)
        ]
    )

    assert all(
        (expected.get_date() == actual.get_date())
        and (expected.get_amount() == actual.get_amount())
        for expected, actual in zip(expected_intervals, generated_payments)
    )


def test_reocurring_payment_builder():
    builder = ReocurringMoneyTransferBuilder()
    builder.set_first_ocurrence(2022)
    builder.set_last_ocurrence(2023)
    builder.set_interval_monthly()
    builder.set_category(Category.OTHER_PAYMENT)
    builder.schedule_money_transfer("MyPayment1", -100.0)
    builder.set_interval(months=2)
    builder.set_category(Category.SALERY)
    builder.schedule_money_transfer("MySalery", 1000.0)

    scheduled_transfers = builder.get_scheduled_transfers()

    assert len(scheduled_transfers) == 2
    assert scheduled_transfers[0].get_money_transfer_amount() == -100.0
    assert scheduled_transfers[0].get_name() == "MyPayment1"
    assert scheduled_transfers[1].get_money_transfer_amount() == 1000.0
    assert scheduled_transfers[1].get_name() == "MySalery"


def test_money_transfer_manager():
    builder = ReocurringMoneyTransferBuilder()
    builder.set_first_ocurrence(2022)
    builder.set_last_ocurrence(2023)
    builder.set_interval_monthly()
    builder.set_category(Category.OTHER_PAYMENT)
    builder.schedule_money_transfer("MyPayment1", -100.0)
    builder.set_interval(months=2)
    builder.set_category(Category.SALERY)
    builder.schedule_money_transfer("MySalery", 1000.0)

    scheduled_transfers = builder.get_scheduled_transfers()

    manager = MoneyTransferVisualizer()
    manager.add_transfers(scheduled_transfers)

    df = manager.to_dataframe(from_date=year(2022), to_date=year(2023))
    print(df)


def test_random_data_plots():

    builder = ReocurringMoneyTransferBuilder()
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
        builder.schedule_money_transfer(f"dummy {i}", amount)

    scheduled_transfers = builder.get_scheduled_transfers()

    manager = MoneyTransferVisualizer()
    manager.add_transfers(scheduled_transfers)
    manager.set_analysis_interval(year(2022), year(2023))

    df = manager._to_dataframe()
    print(df)
