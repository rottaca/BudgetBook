import os.path
import sys
from datetime import date, datetime

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State


# load_figure_template("cosmo")

# pio.templates.default = "cosmo"

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
sys.path.append(SRC_DIR)

from BudgetBook.account_statement_parser import AccountStatementCsvParser
from BudgetBook.bank_transfer_visualizer import BankTransferVisualizer


def year(year: int) -> date:
    return date(year=year, month=1, day=1)


# builder = ReocurringBankTransferBuilder()
# builder.set_first_ocurrence(2022)
# builder.set_last_ocurrence(2023)
# for i in range(10):
#     amount = (random.random() - 0.5) * 1000.0
#     cat = (
#         Category.SALERY#         if amount > 0
#         else Category(random.randint(1, len(Category) - 1))
#     )
#     builder.set_category(cat)
#     builder.set_interval(0, random.randint(1, 5), 0)
#     builder.schedule_bank_transfer(f"dummy {i}", amount)

# scheduled_transfers = builder.get_scheduled_transfers()

csv_parser = AccountStatementCsvParser(
    r"D:\Benutzer\Andreas\Downloads\Umsaetze_2022.05.01.csv",
    "configuration.yaml",
)
scheduled_transfers = csv_parser.to_scheduled_transfers()

manager = BankTransferVisualizer()
manager.add_transfers(scheduled_transfers)

default_start_date, default_end_date = date(year=2021, month=5, day=1), date(
    year=2022, month=5, day=1
)
manager.set_analysis_interval(default_start_date, default_end_date)


def generate_tabs(manager):
    tab1_content = dbc.Card(
        dbc.CardBody(
            [
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
            ]
        ),
        className="mt-3",
    )

    tab2_content = dbc.Card(
        dbc.CardBody(
            [
                dcc.Graph(
                    id="transfers_per_month",
                    figure=manager.plot_transfers_per_month(),
                    style={"height": "80vh"},
                ),
            ]
        ),
        className="mt-3",
    )

    tab3_content = dbc.Card(
        dbc.CardBody(
            [
                dcc.Graph(
                    id="plot_income_per_month",
                    figure=manager.plot_income_per_month(),
                    style={"height": "45vh"},
                ),
                dcc.Graph(
                    id="plot_payments_per_month",
                    figure=manager.plot_payments_per_month(),
                    style={"height": "60vh"},
                ),
            ]
        ),
        className="mt-3",
    )

    return [
        dbc.Tab(tab1_content, label="Overview"),
        dbc.Tab(tab2_content, label="Transfers"),
        dbc.Tab(tab3_content, label="Individual Transfers"),
    ]


input_form = dbc.Form(
    [
        dbc.Row(
            [
                dbc.Label("Date Range", html_for="date-picker-range", width=2),
                dbc.Col(
                    dcc.DatePickerRange(
                        id="date-picker-range",
                        initial_visible_month=datetime.now(),
                        start_date=default_start_date,
                        end_date=default_end_date,
                        display_format="MM/YYYY",
                    ),
                    width=8,
                ),
                dbc.Col(
                    dbc.Button("Update", id="update-button"),
                    width=2,
                ),
            ]
        ),
        dbc.Row(
            dbc.Col(
                dbc.Label("", id="error", width=2),
            )
        ),
    ],
    class_name="m-2",
)
from flask import Flask

server = Flask(__name__)
app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.COSMO])
app.layout = dbc.Container(
    [
        html.H1("Budget Book Dashboard", style={"textAlign": "center"}),
        dbc.Button(
            "Open collapse",
            id="collapse-button",
            className="mb-3",
            color="primary",
            n_clicks=0,
        ),
        dbc.Collapse(
            dbc.Card(dbc.CardBody(input_form)), id="collapse", class_name="pb-1"
        ),
        dbc.Tabs(generate_tabs(manager), id="tabs"),
    ]
)


@app.callback(
    [Output("collapse", "is_open"), Output("collapse-button", "children")],
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    print("collapse called")
    if n:
        return not is_open, "Hide Settings" if not is_open else "Show Settings"
    return is_open, "Show Settings"


@app.callback(
    [Output("tabs", "children"), Output("error", "children")],
    State("date-picker-range", "start_date"),
    State("date-picker-range", "end_date"),
    State("tabs", "children"),
    Input("update-button", "n_clicks"),
)
def update_output(start_date, end_date, curr_tab_children, n_clicks):
    print("Update called")
    if start_date is not None and end_date is not None and start_date < end_date:
        manager.set_analysis_interval(
            datetime.strptime(start_date, "%Y-%m-%d").date(),
            datetime.strptime(end_date, "%Y-%m-%d").date(),
        )
        return generate_tabs(manager), ""
    else:
        return curr_tab_children, "Date Range not valid!"


if __name__ == "__main__":
    app.run_server(debug=False)
