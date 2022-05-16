import base64
import io
import os.path
import sys
from datetime import date, datetime

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, dash_table, no_update
import dash
from dash.dash_table.Format import Format, Scheme, Symbol
from dash.dependencies import Input, Output, State

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
sys.path.append(SRC_DIR)

from BudgetBook.account_statement_parser import AccountStatementCsvParser
from BudgetBook.bank_transfer_visualizer import BankTransferVisualizer
from BudgetBook.config_parser import ConfigParser, DataColumns


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

default_start_date = date(year=2021, month=5, day=1)
default_end_date = date(year=2022, month=5, day=1)

config = ConfigParser("configuration.yaml")
csv_parser = AccountStatementCsvParser(
    r"D:\Benutzer\Andreas\Downloads\Umsaetze_2022.05.01.csv",
    config,
)
scheduled_transfers = csv_parser.to_dated_bank_transfers()

manager = BankTransferVisualizer(config)
manager.add_transfers(scheduled_transfers)

manager.set_analysis_interval(default_start_date, default_end_date)


def generate_tabs(manager: BankTransferVisualizer):
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
                dcc.Graph(
                    id="plot_internal_transfers_per_month",
                    figure=manager.plot_internal_transfers_per_month(),
                    style={"height": "60vh"},
                ),
            ]
        ),
        className="mt-3",
    )

    df = manager.plot_statement_dataframe()
    columns = [
        {
            "id": c,
            "name": c,
            "type": "numeric",
            "format": Format(precision=2, scheme=Scheme.fixed),
        }
        for c in df.columns
    ]

    tab4_content = dbc.Card(
        dbc.CardBody(
            [
                dash_table.DataTable(
                    id="statement-table",
                    columns=columns,
                    data=df.to_dict("records"),
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    page_action="native",
                    page_current=0,
                    page_size=20,
                    style_cell={
                        "minWidth": "50px",
                        "maxWidth": "200px",
                        "whiteSpace": "normal",
                        "height": "auto",
                        "textAlign": "left",
                    },
                )
            ]
        ),
        className="mt-3",
    )

    return [
        dbc.Tab(tab1_content, label="Overview"),
        dbc.Tab(tab2_content, label="Transfers"),
        dbc.Tab(tab3_content, label="Individual Transfers"),
        dbc.Tab(tab4_content, label="Dataset"),
    ]


input_form = dbc.Form(
    [
        dbc.Row(
            dbc.Col(
                dcc.Upload(
                    id="upload-data",
                    children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "margin": "10px",
                    },
                )
            )
        ),
        dbc.Row(
            [
                dbc.Label("Date Range", html_for="date-picker-range", width=2),
                dbc.Col(
                    dcc.DatePickerRange(
                        id="date-picker-range",
                        initial_visible_month=datetime.now(),
                        start_date=default_start_date,
                        end_date=default_end_date,
                        display_format="DD/MM/YYYY",
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

input_form = dbc.Form(
    [
        dbc.Row(
            [
                dbc.Label(
                    "Statement Dataset",
                    html_for="upload-data",
                    width=2,
                ),
                dbc.Col(
                    dcc.Upload(
                        id="upload-data",
                        children=html.Div("Click to upload a csv file."),
                        style={
                            "width": "284px",
                            "height": "60px",
                            "lineHeight": "60px",
                            "borderWidth": "1px",
                            "borderStyle": "dashed",
                            "borderRadius": "5px",
                            "textAlign": "center",
                        },
                    )
                ),
            ],
            class_name="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label(
                    "Select a date range to evaluate",
                    html_for="date-picker-range",
                    width=2,
                ),
                dbc.Col(
                    dcc.DatePickerRange(
                        id="date-picker-range",
                        initial_visible_month=datetime.now(),
                        start_date=default_start_date,
                        end_date=default_end_date,
                        display_format="DD/MM/YYYY",
                    ),
                    width=8,
                ),
            ],
            class_name="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button("Update", id="update-button"),
                    width=2,
                ),
                dbc.Col(
                    dbc.Label("", id="error"),
                    width=8,
                ),
            ],
            class_name="mb-3",
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


def parse_uploaded_csv(contents, filename):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    if "csv" in filename:
        iostream = io.StringIO(decoded.decode("utf-8"))
        csv_parser = AccountStatementCsvParser(
            iostream,
            config,
        )

        manager.clear_transfers()
        manager.add_transfers(csv_parser.to_dated_bank_transfers())
        manager.set_analysis_interval(default_start_date, default_end_date)


@app.callback(
    [Output("collapse", "is_open"), Output("collapse-button", "children")],
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open, "Hide Settings" if not is_open else "Show Settings"
    return is_open, "Show Settings"


@app.callback(
    [
        Output("tabs", "children"),
        Output("date-picker-range", "start_date"),
        Output("date-picker-range", "end_date"),
        Output("error", "children"),
    ],
    State("date-picker-range", "start_date"),
    State("date-picker-range", "end_date"),
    Input("update-button", "n_clicks"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
)
def update_output(start_date, end_date, n_clicks, contents, filename):
    ctx = dash.callback_context

    if not ctx.triggered:
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )

    error_msg = dash.no_update

    # File uploaded?
    if ctx.triggered[0]["prop_id"] == "upload-data.contents":
        if not filename.endswith(".csv"):
            error_msg = "Invalid file type selected. Only CSV is supported!"
        else:
            parse_uploaded_csv(contents, filename)
            if manager.dataset_is_valid():
                start_date = manager._dataframe_cache.index.min().strftime("%Y-%m-%d")
                end_date = manager._dataframe_cache.index.max().strftime("%Y-%m-%d")
                return (
                    dash.no_update,
                    start_date,
                    end_date,
                    "File Uploaded, adjust the date range and click on update!",
                )
            else:
                error_msg = "Internal error!"

    elif ctx.triggered[0]["prop_id"] == "update-button.n_clicks":
        if start_date is not None and end_date is not None and start_date < end_date:
            if manager.dataset_is_valid():
                manager.set_analysis_interval(
                    datetime.strptime(start_date, "%Y-%m-%d").date(),
                    datetime.strptime(end_date, "%Y-%m-%d").date(),
                )
                return (
                    generate_tabs(manager),
                    dash.no_update,
                    dash.no_update,
                    "Data updated!",
                )
            else:
                error_msg = "Internal error!"
        else:
            error_msg = "Date Range not valid!"
    else:
        error_msg = "Invalid trigger!"

    return dash.no_update, dash.no_update, dash.no_update, error_msg


if __name__ == "__main__":

    app.run_server(debug=True)
