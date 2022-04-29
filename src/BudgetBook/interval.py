import copy
import datetime
import pandas as pd
from typing import List
from dateutil.relativedelta import relativedelta

TIMEDELTA_FULL_YEAR = datetime.timedelta(days=365)

CURRENCY_SYMBOL = "Euro"


class DatedMoneyTransfer:
    def __init__(self, name: str, date: datetime.date, amount: float) -> None:
        self._name = name
        self._amount = amount
        self._date = date

    def get_name(self) -> str:
        return self._name

    def get_amount(self) -> float:
        return self._amount

    def get_date(self) -> datetime.date:
        return self._date

    def __str__(self) -> str:
        return f"{self._name}: {self._amount} {CURRENCY_SYMBOL} on {self._date}"

    def __repr__(self) -> str:
        return str(self)


class MoneyTransferInterval:
    def __init__(self, years: int = 0, months: int = 0, days: int = 0) -> None:
        self._interval = relativedelta(years=years, months=months, days=days)

    def to_relative_delta(self) -> relativedelta:
        return self._interval

    @staticmethod
    def monthly():
        return MoneyTransferInterval(months=1)

    @staticmethod
    def quaterly():
        return MoneyTransferInterval(months=4)

    @staticmethod
    def yearly():
        return MoneyTransferInterval(years=1)

    def __str__(self) -> str:
        s = []
        if self._interval.years > 0:
            s.append(f"{self._interval.years} years")
        if self._interval.months > 0:
            s.append(f"{self._interval.months} months")
        if self._interval.days > 0:
            s.append(f"{self._interval.days} days")

        return f"every {' and '.join(s)}"

    def __repr__(self) -> str:
        return str(self)


class ReocurringEvent:
    def __init__(
        self,
        first_occurence: datetime.date,
        interval_size: MoneyTransferInterval,
        last_occurence: datetime.date = None,
    ) -> None:
        self._first_occurence = first_occurence
        self._interval_size = interval_size
        self._last_occurence = last_occurence

    def __str__(self) -> str:
        return f"{self._interval_size} from {self._first_occurence} to {self._last_occurence}"

    def __repr__(self) -> str:
        return str(self)

    def get_first_occurence(self) -> datetime.date:
        return self._first_occurence

    def get_last_occurence(self) -> datetime.date:
        return self._last_occurence

    def get_interval_size(self) -> MoneyTransferInterval:
        return self._interval_size

    def set_first_occurence(self, first_ocurrence: datetime.date):
        self._first_occurence = first_ocurrence

    def set_interval_size(self, interval_size: MoneyTransferInterval):
        self._interval_size = interval_size

    def set_last_occurence(self, last_ocurrence: datetime.date):
        self._last_occurence = last_ocurrence

    def iterate(self, from_date: datetime.date, up_to: datetime.date) -> datetime.date:
        current = max(from_date, self._first_occurence)

        last = self._last_occurence
        if up_to is not None:
            if last is not None:
                if last > up_to:
                    last = up_to
            else:
                last = up_to

        if last is None:
            raise AttributeError("No end date specified for reocurring event!")

        while current <= last:
            yield current
            current = current + self._interval_size.to_relative_delta()


class ReocurringMoneyTransfer:
    def __init__(
        self, name: str, money_transfer_amount: float, reocurrence: ReocurringEvent
    ) -> None:
        self._reocurrence = reocurrence
        self._money_transfer_amount = money_transfer_amount
        self._name = name

    def get_name(self) -> str:
        return self._name

    def get_money_transfer_amount(self) -> str:
        return self._money_transfer_amount

    def get_reocurrence(self) -> ReocurringEvent:
        return self._reocurrence

    def __str__(self) -> str:
        return f"{self._name}: {self._money_transfer_amount} {CURRENCY_SYMBOL} {self._reocurrence}"

    def __repr__(self) -> str:
        return str(self)

    def iterate(self, from_date: datetime.date, up_to: datetime.date) -> DatedMoneyTransfer:
        for current_date in self._reocurrence.iterate(from_date=from_date, up_to=up_to):
            yield DatedMoneyTransfer(self._name, current_date, self._money_transfer_amount)

    def total_money_transfer_one_year(self) -> float:
        dates = [current_date for current_date in self._reocurrence.iterate()]
        total_money_transfer = len(dates) * self._money_transfer_amount
        return total_money_transfer


class ReocurringMoneyTransferBuilder:
    def __init__(self) -> None:
        self._default_recurrence = ReocurringEvent(None, None, None)
        self._scheduled_transfers = []

    def get_scheduled_transfers(self) -> List[ReocurringMoneyTransfer]:
        return self._scheduled_transfers

    def set_first_ocurrence(self, year: int) -> None:
        self._default_recurrence.set_first_occurence(
            datetime.date(year=year, month=1, day=1)
        )

    def set_last_ocurrence(self, year: int) -> None:
        self._default_recurrence.set_last_occurence(
            datetime.date(year=year, month=1, day=1)
        )

    def set_interval(self, years: int = 0, months: int = 0, days: int = 0) -> None:
        self._default_recurrence.set_interval_size(
            MoneyTransferInterval(years=years, months=months, days=days)
        )

    def set_interval_monthly(self) -> None:
        self._default_recurrence.set_interval_size(MoneyTransferInterval.monthly())

    def set_interval_quaterly(self) -> None:
        self._default_recurrence.set_interval_size(MoneyTransferInterval.quaterly())

    def set_interval_yearly(self) -> None:
        self._default_recurrence.set_interval_size(MoneyTransferInterval.yearly())

    def schedule_money_transfer(self, name: str, amount: float):
        self._scheduled_transfers.append(ReocurringMoneyTransfer(
            name, amount, copy.copy(self._default_recurrence)
        ))

        return self._scheduled_transfers[-1]


class MoneyTransferManager:
    def __init__(self) -> None:
        self._scheduled_transfers:List[ReocurringMoneyTransfer]  = []

    def add_transfer(self, transfer: ReocurringMoneyTransfer):
        self._scheduled_transfers.append(transfer)

    def add_transfers(self, transfers: List[ReocurringMoneyTransfer]):
        self._scheduled_transfers.extend(transfers)

    def get_first_transfer_date(self) -> datetime.date:
        return min(d.get_reocurrence().get_first_occurence() for d in self._scheduled_transfers)

    def to_dataframe(self, from_date, to_date):
        indivdual_transfers = []

        for scheduled_transfer in self._scheduled_transfers:
            transfers = [(transfer.get_date(), transfer.get_name(), transfer.get_amount()) for transfer in scheduled_transfer.iterate(from_date=from_date, up_to=to_date)]
            indivdual_transfers.extend(transfers)

        df = pd.DataFrame(indivdual_transfers, columns=["date", "name", "amount"])

        df = df.set_index("date")
        return df


    def get_payments_per_month(self):
        # todo 
        pass
