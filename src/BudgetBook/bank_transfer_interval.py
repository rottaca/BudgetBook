from dateutil.relativedelta import relativedelta


class BankTransferInterval:
    def __init__(self, years: int = 0, months: int = 0, days: int = 0) -> None:
        if years == 0 and months == 0 and days == 0:
            raise AttributeError("Interval has to be larger than 0 days!")
        self._interval = relativedelta(years=years, months=months, days=days)

    def to_relative_delta(self) -> relativedelta:
        return self._interval

    @staticmethod
    def monthly():
        return BankTransferInterval(months=1)

    @staticmethod
    def quaterly():
        return BankTransferInterval(months=4)

    @staticmethod
    def yearly():
        return BankTransferInterval(years=1)

    def __str__(self) -> str:
        s = []
        if self._interval.years > 0:
            s.append(f"{self._interval.years} years")
        if self._interval.months > 0:
            s.append(f"{self._interval.months} months")
        if self._interval.days > 0:
            s.append(f"{self._interval.days} days")

        return f"every {' and '.join(s)}"

    def __repr__(self) -> str:
        return str(self)
