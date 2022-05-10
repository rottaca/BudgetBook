import datetime

from BudgetBook.bank_transfer_interval import BankTransferInterval


class RegularEvent:
    def __init__(
        self,
        first_occurence: datetime.date,
        interval_size: BankTransferInterval,
        last_occurence: datetime.date = None,
    ) -> None:
        self._first_occurence = first_occurence
        self._interval_size = interval_size
        self._last_occurence = last_occurence

    def __str__(self) -> str:
        if self._last_occurence is not None:
            if self._interval_size is not None:
                return f"{self._interval_size} from {self._first_occurence} to {self._last_occurence}"
            else:
                assert False
        else:
            if self._interval_size is not None:
                return f"{self._interval_size} starting from {self._first_occurence}"
            else:
                return f"on {self._first_occurence}"

    def __repr__(self) -> str:
        return str(self)

    def get_first_occurence(self) -> datetime.date:
        return self._first_occurence

    def get_last_occurence(self) -> datetime.date:
        return self._last_occurence

    def get_interval_size(self) -> BankTransferInterval:
        return self._interval_size

    def set_first_occurence(self, first_ocurrence: datetime.date):
        self._first_occurence = first_ocurrence

    def set_interval_size(self, interval_size: BankTransferInterval):
        self._interval_size = interval_size

    def set_last_occurence(self, last_ocurrence: datetime.date):
        self._last_occurence = last_ocurrence

    def iterate(self, from_date: datetime.date, up_to: datetime.date) -> datetime.date:

        if up_to is None:
            raise AttributeError("No end date specified for Regular event!")
        if from_date is None:
            raise AttributeError("No start date specified for Regular event!")

        current = self._first_occurence  # max(from_date, self._first_occurence)

        if self._interval_size is None:
            if current >= from_date and current < up_to:
                yield current
        else:
            while current < up_to:
                if current >= from_date:
                    yield current

                current = current + self._interval_size.to_relative_delta()

        return None
