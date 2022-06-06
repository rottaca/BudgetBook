from dateutil.relativedelta import relativedelta
import pandas as pd

class TransactionInterval(relativedelta):
    def __init__(self, years: int = 0, months: int = 0, days: int = 0) -> None:
        super().__init__(years=years, months=months, days=days)
        if years == 0 and months == 0 and days == 0:
            raise AttributeError("Interval has to be larger than 0 days!")

    @staticmethod
    def fromTimeDelta(delta: pd.Timedelta):
        return TransactionInterval(days=delta.days)

    @staticmethod
    def monthly():
        return TransactionInterval(months=1)

    @staticmethod
    def quaterly():
        return TransactionInterval(months=4)

    @staticmethod
    def yearly():
        return TransactionInterval(years=1)

    def __str__(self) -> str:
        s = []
        if self.years > 0:
            s.append(f"{self.years} years")
        if self.months > 0:
            s.append(f"{self.months} months")
        if self.days > 0:
            s.append(f"{self.days} days")

        return f"every {' and '.join(s)}"

    def __repr__(self) -> str:
        return str(self)
