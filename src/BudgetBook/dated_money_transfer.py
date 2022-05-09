import datetime

from BudgetBook.helper import CURRENCY_SYMBOL


class DatedMoneyTransfer:
    def __init__(
        self,
        name: str,
        desc: str,
        category: str,
        date: datetime.date,
        amount: float,
    ) -> None:
        self._name = name
        self._desc = desc
        self._amount = amount
        self._date = date
        self._category = category

    def get_category(self) -> str:
        return self._category

    def get_name(self) -> str:
        return self._name

    def get_desc(self) -> str:
        return self._desc

    def get_amount(self) -> float:
        return self._amount

    def get_date(self) -> datetime.date:
        return self._date

    def __str__(self) -> str:
        return f"{self._name}: {self._amount} {CURRENCY_SYMBOL} on {self._date}"

    def __repr__(self) -> str:
        return str(self)
