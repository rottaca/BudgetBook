import datetime
from typing import Tuple
from BudgetBook.config_parser import DataColumns

from BudgetBook.helper import CURRENCY_SYMBOL


class DatedTransaction:
    def __init__(
        self,
        payment_party: str,
        date: datetime.date,
        amount: float,
        desc: str = "",
        category: str = "",
    ) -> None:
        self.category = category
        self.date = date
        self.amount = amount
        self.desc = desc
        self.payment_party = payment_party

    def to_dict(self) -> Tuple:
        return {
            DataColumns.PAYMENT_PARTY: self.payment_party,
            DataColumns.DATE: self.date,
            DataColumns.AMOUNT: self.amount,
            DataColumns.DESCRIPTION: self.desc,
            DataColumns.CATEGORY: self.category,
        }

    def __str__(self) -> str:
        return f"{self.payment_party}: {self.amount} {CURRENCY_SYMBOL} on {self.date}"

    def __repr__(self) -> str:
        return str(self)
