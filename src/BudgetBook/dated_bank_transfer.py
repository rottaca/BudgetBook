import datetime
from typing import Tuple

from BudgetBook.helper import CURRENCY_SYMBOL


class DatedBankTransfer:
    def __init__(
        self,
        payment_party: str,
        date: datetime.date,
        amount: float,
        desc: str = "",
        category: str = "unknown",
    ) -> None:
        self.category = category
        self.date = date
        self.amount = amount
        self.desc = desc
        self.payment_party = payment_party

    def to_dict(self) -> Tuple:
        return {
            "payment_party": self.payment_party,
            "date": self.date,
            "amount": self.amount,
            "desc": self.desc,
            "category": self.category,
        }

    def __str__(self) -> str:
        return f"{self.payment_party}: {self.amount} {CURRENCY_SYMBOL} on {self.date}"

    def __repr__(self) -> str:
        return str(self)
