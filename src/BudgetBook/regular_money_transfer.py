import datetime
from BudgetBook.dated_money_transfer import DatedMoneyTransfer
from BudgetBook.helper import CURRENCY_SYMBOL, Category
from BudgetBook.regular_event import RegularEvent


class RegularMoneyTransfer:
    def __init__(
        self,
        name: str,
        category: Category,
        money_transfer_amount: float,
        reocurrence: RegularEvent,
        desc: str = "",
    ) -> None:
        self._reocurrence = reocurrence
        self._money_transfer_amount = money_transfer_amount
        self._category = category
        self._name = name
        self._desc = desc

    def get_name(self) -> str:
        return self._name

    def get__desc(self) -> str:
        return self._desc

    def get_category(self) -> str:
        return self._category

    def get_money_transfer_amount(self) -> str:
        return self._money_transfer_amount

    def get_reocurrence(self) -> RegularEvent:
        return self._reocurrence

    def __str__(self) -> str:
        return f"{self._name}: {self._money_transfer_amount} {CURRENCY_SYMBOL} {self._reocurrence}"

    def __repr__(self) -> str:
        return str(self)

    def iterate(
        self, from_date: datetime.date, up_to: datetime.date
    ) -> DatedMoneyTransfer:
        for current_date in self._reocurrence.iterate(from_date=from_date, up_to=up_to):
            yield DatedMoneyTransfer(
                self._name,
                self._desc,
                self._category,
                current_date,
                self._money_transfer_amount,
            )
