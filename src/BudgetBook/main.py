from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from datetime import date
from pprint import pprint
import random
import sys, os.path
import pandas as pd
import plotly.io as pio

# load_figure_template("cosmo")

# pio.templates.default = "cosmo"

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(SRC_DIR)

from BudgetBook.interval import (
    Category,
    MoneyTransferManager,
    AccountStatementCsvParser,
)


def year(year: int) -> date:
    return date(year=year, month=1, day=1)


# builder = ReocurringMoneyTransferBuilder()
# builder.set_first_ocurrence(2022)
# builder.set_last_ocurrence(2023)
# for i in range(10):
#     amount = (random.random() - 0.5) * 1000.0
#     cat = (
#         Category.SALERY
#         if amount > 0
#         else Category(random.randint(1, len(Category) - 1))
#     )
#     builder.set_category(cat)
#     builder.set_interval(0, random.randint(1, 5), 0)
#     builder.schedule_money_transfer(f"dummy {i}", amount)

# scheduled_transfers = builder.get_scheduled_transfers()

csv_parser = AccountStatementCsvParser(
    r"D:\Benutzer\Andreas\Downloads\Umsaetze_2022.05.01.csv"
)
scheduled_transfers = csv_parser.to_scheduled_transfers()

manager = MoneyTransferManager()
manager.add_transfers(scheduled_transfers)
manager.set_analysis_interval(
    date(year=2021, month=5, day=1), date(year=2022, month=5, day=1)
)

app = Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

if __name__ == "__main__":
    app.layout = dbc.Container(
        [
            html.H1("Budget Book Dashboard", style={"textAlign": "center"}),
            dbc.Container(
                [
                    dbc.Row(
                        dbc.Col(
                            dcc.Graph(
                                id="transfers_per_month",
                                figure=manager.plot_transfers_per_month(),
                                style={"height": "70vh"},
                            )
                        )
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Graph(
                                    id="balance_per_month",
                                    figure=manager.plot_balance_per_month(),
                                )
                            ),
                            dbc.Col(
                                dcc.Graph(
                                    id="pie_chart_per_cateogry",
                                    figure=manager.plot_pie_chart_per_cateogry(),
                                )
                            ),
                        ]
                    ),
                    dbc.Row(
                        dbc.Col(
                            dcc.Graph(
                                id="plot_payments_per_month",
                                figure=manager.plot_payments_per_month(),
                                style={"height": "90vh"},
                            )
                        )
                    ),
                ]
            ),
        ],
        fluid=True,
    )

    app.run_server(debug=False)
