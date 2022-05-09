import datetime
import enum


TIMEDELTA_FULL_YEAR = datetime.timedelta(days=365)

CURRENCY_SYMBOL = "Euro"


@enum.unique
class Category(enum.Enum):
    SALERY = 0
    UNKNOWN_INCOME = 1
    UNKNOWN_PAYMENT = 2
    INSURANCE = 3
    MOBILITY = 4
    HOUSHOLD = 5
    TAX = 6
