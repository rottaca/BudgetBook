import datetime
from typing import List
from BudgetBook.helper import Category
from BudgetBook.money_transfer_interval import MoneyTransferInterval
from BudgetBook.regular_event import RegularEvent
from BudgetBook.regular_money_transfer import RegularMoneyTransfer


class RegularMoneyTransferBuilder:
    def __init__(self) -> None:
        self._current_recurrence = RegularEvent(None, None, None)
        self._scheduled_transfers = []
        self._current_category = Category.UNKNOWN

    def get_scheduled_transfers(self) -> List[RegularMoneyTransfer]:
        return self._scheduled_transfers

    def set_first_ocurrence(self, year: int) -> None:
        self._current_recurrence.set_first_occurence(
            datetime.date(year=year, month=1, day=1)
        )

    def set_last_ocurrence(self, year: int) -> None:
        self._current_recurrence.set_last_occurence(
            datetime.date(year=year, month=1, day=1)
        )

    def set_interval(self, years: int = 0, months: int = 0, days: int = 0) -> None:
        self._current_recurrence.set_interval_size(
            MoneyTransferInterval(years=years, months=months, days=days)
        )

    def set_interval_monthly(self) -> None:
        self._current_recurrence.set_interval_size(MoneyTransferInterval.monthly())

    def set_interval_quaterly(self) -> None:
        self._current_recurrence.set_interval_size(MoneyTransferInterval.quaterly())

    def set_interval_yearly(self) -> None:
        self._current_recurrence.set_interval_size(MoneyTransferInterval.yearly())

    def set_category(self, category: Category) -> None:
        self._current_category = category

    def schedule_money_transfer(self, name: str, amount: float):
        self._scheduled_transfers.append(
            RegularMoneyTransfer(
                name,
                self._current_category,
                amount,
                copy.copy(self._current_recurrence),
            )
        )

        return self._scheduled_transfers[-1]
