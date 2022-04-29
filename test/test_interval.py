from datetime import date
from pprint import pprint
import sys, os.path
import pandas as pd
pd.options.plotting.backend = "plotly"

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(SRC_DIR)

from BudgetBook.interval import (
    DatedMoneyTransfer,
    MoneyTransferManager,
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

    generated_intervals = [i for i in interval.iterate(from_date=year(2022), up_to=year(2023))]
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
        100.0,
        ReocurringEvent(
            first_occurence=year(2022), interval_size=MoneyTransferInterval.monthly()
        ),
    )

    generated_payments = [
        p for p in reocurring_payment.iterate(from_date=year(2022), up_to=date(year=2023, month=5, day=1))
    ]
    expected_intervals = [
        DatedMoneyTransfer(date(year=2022, month=i, day=1), 100.0) for i in range(1, 13)
    ]
    expected_intervals.extend(
        [DatedMoneyTransfer(date(year=2023, month=i, day=1), 100.0) for i in range(1, 5)]
    )

    #pprint(generated_payments)

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

    builder.schedule_money_transfer("MyPayment1", -100.0)
    builder.set_interval(months=2)
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

    builder.schedule_money_transfer("MyPayment1", -100.0)
    builder.set_interval(months=2)
    builder.schedule_money_transfer("MySalery", 1000.0)

    scheduled_transfers = builder.get_scheduled_transfers()

    manager = MoneyTransferManager()
    manager.add_transfers(scheduled_transfers)

    df = manager.to_dataframe(from_date=year(2022), to_date=year(2023))
    print(df)
    
    df_transfers_per_month = df.reset_index().set_index(["date", "name"]).unstack().droplevel(level=0, axis=1)
    df_balence_per_month = df.reset_index().groupby("date").sum()

    
    df_transfers_per_month.plot.bar().show()




