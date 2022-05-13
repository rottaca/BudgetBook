import datetime
from BudgetBook.dated_bank_transfer import DatedBankTransfer
from BudgetBook.helper import CURRENCY_SYMBOL
from BudgetBook.regular_event import RegularEvent


class RegularBankTransfer:
    def __init__(
        self,
        payment_party: str,
        frequency: RegularEvent,
        amount: float,
        category: str = "",
        desc: str = "",
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

    def iterate(
        self, from_date: datetime.date, up_to: datetime.date
    ) -> DatedBankTransfer:
        for current_date in self._frequency.iterate(from_date=from_date, up_to=up_to):
            yield DatedBankTransfer(
                self._payment_party,
                current_date,
                self._amount,
                self._desc,
                self._category,
            )
