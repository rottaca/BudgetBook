import copy
import datetime
from typing import List
from BudgetBook.helper import Category
from BudgetBook.bank_transfer_interval import BankTransferInterval
from BudgetBook.regular_event import RegularEvent
from BudgetBook.regular_bank_transfer import RegularBankTransfer


class RegularBankTransferBuilder:
    def __init__(self) -> None:
        self._current_recurrence = RegularEvent(None, None, None)
        self._scheduled_transfers = []
        self._current_category = None

    def get_scheduled_transfers(self) -> List[RegularBankTransfer]:
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
            BankTransferInterval(years=years, months=months, days=days)
        )

    def set_interval_monthly(self) -> None:
        self._current_recurrence.set_interval_size(BankTransferInterval.monthly())

    def set_interval_quaterly(self) -> None:
        self._current_recurrence.set_interval_size(BankTransferInterval.quaterly())

    def set_interval_yearly(self) -> None:
        self._current_recurrence.set_interval_size(BankTransferInterval.yearly())

    def set_category(self, category: str) -> None:
        self._current_category = category

    def schedule_bank_transfer(
        self,
        payment_party: str,
        amount: float,
        desc: str = "",
    ):
        self._scheduled_transfers.append(
            RegularBankTransfer(
                payment_party,
                copy.copy(self._current_recurrence),
                amount,
                self._current_category,
                desc,
            )
        )
