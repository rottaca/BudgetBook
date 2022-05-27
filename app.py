import base64
import io
import os.path
import sys
import plotly
from datetime import date, datetime
import pandas as pd
from dateutil.relativedelta import relativedelta

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, dash_table, no_update
import dash
from dash.dash_table.Format import Format, Scheme, Symbol
from dash.dependencies import Input, Output, State


SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
sys.path.append(SRC_DIR)

from BudgetBook.account_statement_parser import AccountStatementCsvParser
from BudgetBook.transaction_visualizer import TransactionVisualizer
from BudgetBook.config_parser import (
    DATA_COLUMN_TO_DISPLAY_NAME,
    ConfigParser,
    DataColumns,
)
from BudgetBook.regular_transaction_predictor import RegularTransactionPredictor


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

# scheduled_transactions = builder.get_scheduled_transactions()

default_start_date = date(year=2021, month=5, day=1)
default_end_date = date(year=2022, month=5, day=1)

config = ConfigParser("configuration.yaml")
# csv_parser = AccountStatementCsvParser(
#     r"C:\Users\Andreas Rottach\Google Drive\Umsaetze_2022.05.01.csv",
#     config,
# )
# scheduled_transactions = csv_parser.to_dated_transactions()

# global_transaction_visualizer = TransactionVisualizer(config)
# global_transaction_visualizer.add_transactions(scheduled_transactions)
# global_transaction_visualizer.set_analysis_interval(
#     default_start_date, default_end_date
# )


def generate_tabs(manager: TransactionVisualizer):
    if manager is not None:
        tab1_content = generate_overview_tab(manager)
        tab2_content = generate_transactions_per_category_tab(manager)
        tab3_content = generate_detailed_transactions_tab(manager)
        tab4_content = generate_dataset_table_tab(manager)
        tab5_content = generate_prediction_tab(manager)
    else:
        tab1_content = dbc.Card(dbc.CardBody("Load an account statement (*.csv)"))
        tab2_content = dbc.Card(dbc.CardBody("Load an account statement (*.csv)"))
        tab3_content = dbc.Card(dbc.CardBody("Load an account statement (*.csv)"))
        tab4_content = dbc.Card(dbc.CardBody("Load an account statement (*.csv)"))
        tab5_content = dbc.Card(dbc.CardBody("Load an account statement (*.csv)"))

    return [
        dbc.Tab(tab1_content, label="Overview"),
        dbc.Tab(tab2_content, label="Transfers"),
        dbc.Tab(tab3_content, label="Individual Transfers"),
        dbc.Tab(tab4_content, label="Dataset"),
        dbc.Tab(tab5_content, label="Predictions"),
    ]


def hex_to_rgb(value):
    value = value.lstrip("#")
    lv = len(value)
    return tuple(int(value[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))


def rgb_to_gray(rgb):
    return (rgb[0] + rgb[1] + rgb[2]) / 3


def generate_dataset_table_tab(manager: TransactionVisualizer):
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
    id_amount_column = DATA_COLUMN_TO_DISPLAY_NAME[DataColumns.AMOUNT]
    id_category_column = DATA_COLUMN_TO_DISPLAY_NAME[DataColumns.CATEGORY]

    style_rules_for_categories = [
        {
            "if": {
                "filter_query": f"{{{id_category_column}}} = '{category}'",
                "column_id": id_category_column,
            },
            "backgroundColor": color,
            "color": "white" if rgb_to_gray(hex_to_rgb(color)) < 128 else "black",
        }
        for category, color in manager.category_to_color_map.items()
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
                        "whiteSpace": "pre-line",
                        "height": "auto",
                        "textAlign": "left",
                    },
                    style_table={
                        "width": "100%",
                    },
                    style_data_conditional=[
                        {
                            "if": {
                                "filter_query": f"{{{id_amount_column}}} < 0",
                                "column_id": id_amount_column,
                            },
                            "backgroundColor": "tomato",
                            "color": "white",
                        },
                        {
                            "if": {
                                "filter_query": f"{{{id_amount_column}}} > 0",
                                "column_id": id_amount_column,
                            },
                            "backgroundColor": "green",
                            "color": "white",
                        },
                        *style_rules_for_categories,
                    ],
                )
            ]
        ),
        className="mt-3",
    )

    return tab4_content


def generate_detailed_transactions_tab(manager: TransactionVisualizer):

    fig = plotly.subplots.make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(
            "Income Per Month",
            "Payments Per Month",
            "Internal Transfers Per Month",
        ),
    )

    manager.plot_income_per_month(fig=fig, row=1, col=1)
    manager.plot_payments_per_month(fig=fig, row=2, col=1)
    manager.plot_internal_transactions_per_month(fig=fig, row=3, col=1)

    fig.update_layout(legend=dict(yanchor="top", y=0.70, xanchor="left", x=1.01))

    tab3_content = dbc.Card(
        dbc.CardBody(
            [
                dcc.Graph(
                    id="plot_details",
                    figure=fig,
                    style={"height": "1400px"},
                ),
            ]
        ),
        className="mt-3",
    )

    return tab3_content


def generate_transactions_per_category_tab(manager: TransactionVisualizer):
    tab_content = dbc.Card(
        dbc.CardBody(
            [
                dcc.Graph(
                    id="transactions_per_month",
                    figure=manager.plot_transactions_per_month(),
                    style={"height": "80vh"},
                ),
            ]
        ),
        className="mt-3",
    )
    return tab_content


def generate_overview_tab(manager: TransactionVisualizer):
    tab_content = dbc.Card(
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
                dbc.Row(
                    dbc.Col(
                        dcc.Graph(
                            id="category_variance",
                            figure=manager.plot_cateogory_variance(),
                            style={"height": "900px"},
                        )
                    )
                ),
            ]
        ),
        className="mt-3",
    )

    return tab_content


def generate_prediction_tab(manager: TransactionVisualizer):
    predictor = RegularTransactionPredictor(config)
    regular_transactions = predictor.to_regular_transactions(manager.get_transactions())
    df = pd.DataFrame.from_records([t.to_dict() for t in regular_transactions])

    df.rename(columns=DATA_COLUMN_TO_DISPLAY_NAME, inplace=True)

    columns = [
        {
            "id": c,
            "name": c,
            "type": "numeric",
            "format": Format(precision=2, scheme=Scheme.fixed),
        }
        for c in df.columns
    ]

    id_amount_column = DATA_COLUMN_TO_DISPLAY_NAME[DataColumns.AMOUNT]
    id_category_column = DATA_COLUMN_TO_DISPLAY_NAME[DataColumns.CATEGORY]

    style_rules_for_categories = [
        {
            "if": {
                "filter_query": f"{{{id_category_column}}} = '{category}'",
                "column_id": id_category_column,
            },
            "backgroundColor": color,
            "color": "white" if rgb_to_gray(hex_to_rgb(color)) < 128 else "black",
        }
        for category, color in manager.category_to_color_map.items()
    ]

    tab5_content = dbc.Card(
        dbc.CardBody(
            [
                dash_table.DataTable(
                    id="prediction-table",
                    columns=columns,
                    data=df.to_dict("records"),
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    page_action="native",
                    page_current=0,
                    page_size=20,
                    style_cell={
                        "whiteSpace": "pre-line",
                        "height": "auto",
                        "textAlign": "left",
                    },
                    style_table={
                        "width": "100%",
                    },
                    style_data_conditional=[
                        {
                            "if": {
                                "filter_query": f"{{{id_amount_column}}} < 0",
                                "column_id": id_amount_column,
                            },
                            "backgroundColor": "tomato",
                            "color": "white",
                        },
                        {
                            "if": {
                                "filter_query": f"{{{id_amount_column}}} > 0",
                                "column_id": id_amount_column,
                            },
                            "backgroundColor": "green",
                            "color": "white",
                        },
                        *style_rules_for_categories,
                    ],
                )
            ]
        ),
        className="mt-3",
    )

    return tab5_content


def generate_input_form(default_start_date, default_end_date):
    input_form = dbc.Form(
        [
            dbc.Row(
                [
                    dbc.Label(
                        "Upload your statement(s) for analysis (*.csv)",
                        html_for="upload-data",
                        style={"font-weight": "bold"},
                    ),
                    dbc.Col(
                        dcc.Upload(
                            id="upload-data",
                            children=html.Div(
                                "Click or drag-and-drop to upload CSV files."
                            ),
                            multiple=True,
                            style={
                                "height": "50px",
                                "lineHeight": "50px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "5px",
                                "textAlign": "center",
                            },
                        ),
                    ),
                    dbc.Label(
                        "",
                        html_for="upload-data",
                        id="file-uploaded-label",
                    ),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Label(
                        "Select the time interval you want to evaluate",
                        html_for="date-picker-range",
                        style={"font-weight": "bold"},
                    ),
                    dbc.Col(
                        dcc.DatePickerRange(
                            id="date-picker-range",
                            initial_visible_month=datetime.now(),
                            start_date=default_start_date,
                            end_date=default_end_date,
                            display_format="DD/MM/YYYY",
                        ),
                    ),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                html.Div("", id="status", className="fade alert alert-danger hide"),
                class_name="mb-3",
            ),
        ],
        class_name="m-2",
    )

    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Upload Dataset"), close_button=True),
            dbc.ModalBody(input_form),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Update",
                        id="update-button",
                        className="ms-auto",
                    ),
                ]
            ),
        ],
        id="modal",
        size="lg",
        is_open=False,
    )


from flask import Flask

server = Flask(__name__)
app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.COSMO])

app.layout = dbc.Container(
    [
        html.H1("Budget Book Dashboard", style={"textAlign": "center"}),
        dbc.Button(
            "Open Settings",
            id="open-settings-button",
            className="mb-3",
            color="primary",
            n_clicks=0,
        ),
        dbc.Spinner(
            children=generate_input_form(default_start_date, default_end_date),
            type="border",
            color="primary",
            fullscreen=True,
            delay_hide=200,
            spinner_style={"width": "10rem", "height": "10rem"},
        ),
        dbc.Tabs(generate_tabs(None), id="tabs"),
    ],
    style={"width": "80vw", "minWidth": "80vw"},
)


def uploaded_csv_to_iostream(contents, filename):
    if ".csv" not in filename:
        return

    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    iostream = io.StringIO(decoded.decode("utf-8"))
    return iostream


@app.callback(
    Output("modal", "is_open"),
    Input("open-settings-button", "n_clicks"),
    State("modal", "is_open"),
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open


@app.callback(
    [
        Output("tabs", "children"),
        Output("date-picker-range", "start_date"),
        Output("date-picker-range", "end_date"),
        Output("status", "children"),
        Output("status", "className"),
    ],
    State("date-picker-range", "start_date"),
    State("date-picker-range", "end_date"),
    Input("update-button", "n_clicks"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("status", "className"),
)
def update_output(start_date, end_date, n_clicks, contents, filenames, status_cls):
    ctx = dash.callback_context

    if not ctx.triggered:
        return dash.no_update

    output_tabs = dash.no_update
    datepicker_start_date = dash.no_update
    datepicker_end_date = dash.no_update
    status_text = ""
    status_class = status_cls.replace("show", "hide")

    def set_error(msg):
        cls = status_class.replace("hide", "show")
        cls = cls.replace("alert-success", "alert-danger")
        return msg, cls

    def set_success(msg):
        cls = status_class.replace("hide", "show")
        cls = cls.replace("alert-danger", "alert-success")
        return msg, cls

    if isinstance(filenames, str):
        filenames = [filenames]
    if isinstance(contents, str):
        contents = [contents]

    # File uploaded?
    if ctx.triggered[0]["prop_id"] == "upload-data.contents":
        invalid_filename = False
        for filename in filenames:
            if not filename.endswith(".csv"):
                status_text, status_class = set_error(
                    "Invalid file type selected. Only CSV is supported!"
                )
                invalid_filename = True
                break

        if not invalid_filename:
            dfs = []
            for filename, content in zip(filenames, contents):
                parser = AccountStatementCsvParser(
                    uploaded_csv_to_iostream(content, filename),
                    config,
                )
                dfs.append(parser.get_csv_dataframe())

            df = pd.concat(dfs)
            datepicker_start_date = df[DataColumns.DATE].min().strftime("%Y-%m-%d")
            datepicker_end_date = df[DataColumns.DATE].max().strftime("%Y-%m-%d")

            status_text, status_class = set_success(
                f"{len(filenames)} file(s) selected for analysis. Pick a time range and click on update!"
            )

    elif ctx.triggered[0]["prop_id"] == "update-button.n_clicks":
        if start_date is None or end_date is None or start_date >= end_date:
            status_text, status_class = set_error("Date Range not valid!")
        elif filenames is None:
            status_text, status_class = set_error("No files have been selected!")
        else:
            dfs = []
            for filename, content in zip(filenames, contents):
                iostream = uploaded_csv_to_iostream(content, filename)

                csv_df = AccountStatementCsvParser(
                    iostream,
                    config,
                ).get_csv_dataframe()

                dfs.append(csv_df)

            csv_parser = AccountStatementCsvParser(
                pd.concat(dfs),
                config,
            )
            status_text, status_class = set_success(
                f"{len(filenames)} file(s) uploaded succesfully. Pick a time range and click on update!"
            )

            transaction_visualizer = TransactionVisualizer(config)
            transaction_visualizer.set_transactions(csv_parser.to_dated_transactions())

            transaction_visualizer.set_analysis_interval(
                datetime.strptime(start_date, "%Y-%m-%d").date(),
                datetime.strptime(end_date, "%Y-%m-%d").date() + relativedelta(days=1),
            )
            if transaction_visualizer.dataset_is_valid():
                output_tabs = generate_tabs(transaction_visualizer)
                status_text, status_class = set_success("Data visualization updated!")
            else:
                status_text, status_class = set_error("Internal error!")
    else:
        status_text, status_class = set_error("Invalid trigger!")

    return (
        output_tabs,
        datepicker_start_date,
        datepicker_end_date,
        status_text,
        status_class,
    )


if __name__ == "__main__":

    app.run_server(debug=True)
