from datetime import date
import os.path
import random
import sys

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
sys.path.append(SRC_DIR)

from BudgetBook.regular_transaction_builder import RegularTransactionBuilder

def build_dataset():
    builder = RegularTransactionBuilder()
    builder.set_first_ocurrence(year=2022)
    builder.set_last_ocurrence(year=2023)

    builder.set_category("Salary")
    builder.set_interval_monthly()
    builder.build_regular_transaction("Corporation", 3000.0, "Salery for Employee 1234567")
    builder.build_dated_transaction("Income from XY", 500.0, date(2022, 4, 26), "")

    builder.set_category("Appartment")
    builder.set_interval_monthly()
    builder.build_regular_transaction("Rent", -1000.0, "Rent for appartment XY")
    builder.build_regular_transaction("Electricity", -60.0, "Electricty payment for customer 4534525")
    builder.build_regular_transaction("Water", -30.0, "Water payment for customer 3252563")

    builder.set_category("Insurance")
    builder.set_interval_quaterly()
    builder.build_regular_transaction("Car Insurance", -200.0, "Insurance for Car XY")
    builder.set_interval_monthly()
    builder.build_regular_transaction("My Other Insurance", -150.0, "Insurance for XY")

    builder.set_category("Internet and Mobile")
    builder.set_interval_monthly()
    builder.build_regular_transaction("Mobile Phone Contract XY", -30.0, "Customer 0987654")
    builder.build_regular_transaction("Home Internet", -50.0, "XL Plan Monthly Payment")

    builder.set_category("Mobility")
    builder.set_interval_monthly()
    builder.build_regular_transaction("Gas Station", -80.0, "Thank you for choosing XY!")
    builder.set_interval_yearly()
    builder.build_regular_transaction("Car Dealership", -300.0, "Vehicle Inspection for XY")
    builder.build_dated_transaction("Car Dealership", -1200.0, date(2022, 4, 27), "Car repair for XY")

    builder.set_category("Savings")
    builder.set_interval_monthly()
    builder.build_regular_transaction("Savings", -1000.0, "Regular Savings")

    builder.set_category("Vacation")
    builder.build_dated_transaction("Vacation in Hawaii", -3000.0, date(2022, 8, 5),"Yearly 3 week vacation!")

    builder.set_category("Groceries")
    for i in range(5):
        for month in range(1, 13):
            builder.build_dated_transaction("Shopping at XY", -random.random() * 100, date(2022, month, random.randint(1, 28)))

    return builder.transactions_to_dataframe()