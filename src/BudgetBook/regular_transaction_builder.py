import copy
import datetime
from typing import List
from BudgetBook.transaction_interval import TransactionInterval
from BudgetBook.regular_event import RegularEvent
from BudgetBook.regular_transaction import RegularTransaction
from BudgetBook.dated_transaction import DatedTransaction

class RegularTransactionBuilder:
    def __init__(self) -> None:
        self._current_recurrence = RegularEvent(None, None, None)
        self._scheduled_transactions = []
        self._current_category = None

    def transactions_to_dataframe(self) -> List[RegularTransaction]:
        return self._scheduled_transactions

    def set_first_ocurrence(self, year: int, month:int = 1, day:int = 1) -> None:
        self._current_recurrence.set_first_occurence(
            datetime.date(year=year, month=month, day=day)
        )

    def set_last_ocurrence(self, year: int) -> None:
        self._current_recurrence.set_last_occurence(
            datetime.date(year=year, month=1, day=1)
        )

    def set_interval(self, years: int = 0, months: int = 0, days: int = 0) -> None:
        self._current_recurrence.set_interval_size(
            TransactionInterval(years=years, months=months, days=days)
        )

    def set_interval_monthly(self) -> None:
        self._current_recurrence.set_interval_size(TransactionInterval.monthly())

    def set_interval_quaterly(self) -> None:
        self._current_recurrence.set_interval_size(TransactionInterval.quaterly())

    def set_interval_yearly(self) -> None:
        self._current_recurrence.set_interval_size(TransactionInterval.yearly())

    def set_category(self, category: str) -> None:
        self._current_category = category

    def build_regular_transaction(
        self,
        payment_party: str,
        amount: float,
        desc: str = "",
    ):
        self._scheduled_transactions.append(
            RegularTransaction(
                payment_party,
                copy.copy(self._current_recurrence),
                amount,
                desc,
                self._current_category,
            )
        )

    def build_dated_transaction(
        self,
        payment_party: str,
        amount: float,
        date_of_transaction: datetime.date,
        desc: str = "",
    ):
        self._scheduled_transactions.append(
            DatedTransaction(
                payment_party,
                date_of_transaction,
                amount,
                desc,
                self._current_category,
            )
        )
