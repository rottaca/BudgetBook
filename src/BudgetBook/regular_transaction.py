import datetime

from BudgetBook.config_parser import DataColumns
from BudgetBook.dated_transaction import DatedTransaction
from BudgetBook.helper import CURRENCY_SYMBOL
from BudgetBook.regular_event import RegularEvent


class RegularTransaction:
    def __init__(
        self,
        payment_party: str,
        frequency: RegularEvent,
        amount: float,
        desc: str = "",
        category: str = "",
    ) -> None:
        self._frequency = frequency
        self._amount = amount
        self._category = category
        self._desc = desc
        self._payment_party = payment_party

    def __str__(self) -> str:
        return (
            f"{self._payment_party}: {self._amount} {CURRENCY_SYMBOL} {self._frequency}"
        )

    def __repr__(self) -> str:
        return str(self)

    def get_frequency(self) -> RegularEvent:
        return self._frequency

    def to_dict(self) -> dict:
        return {
            DataColumns.PAYMENT_PARTY: self._payment_party,
            "Frequency": str(self._frequency),
            DataColumns.AMOUNT: self._amount,
            DataColumns.DESCRIPTION: self._desc,
            DataColumns.CATEGORY: self._category,
        }

    def iterate(
        self, from_date: datetime.date, up_to: datetime.date
    ) -> DatedTransaction:
        for current_date in self._frequency.iterate(from_date=from_date, up_to=up_to):
            yield DatedTransaction(
                self._payment_party,
                current_date,
                self._amount,
                self._desc,
                self._category,
            )
