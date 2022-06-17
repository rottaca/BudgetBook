import base64
import io
import os.path
import sys
import plotly
from plotly.subplots import make_subplots

from datetime import date, datetime
import pandas as pd
from dateutil.relativedelta import relativedelta
import argparse

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
    Config,
    DataColumns,
)
from BudgetBook.regular_transaction_predictor import RegularTransactionPredictor


def year(year: int) -> date:
    return date(year=year, month=1, day=1)

default_start_date = date.today()
default_end_date = date.today()

enable_predictions = False

def generate_tabs(manager: TransactionVisualizer, with_predictions_tab):
    if manager is not None:
        tab1_content = generate_overview_tab(manager)
        tab2_content = generate_transactions_per_category_tab(manager)
        tab3_content = generate_detailed_transactions_tab(manager)
        tab4_content = generate_dataset_table_tab(manager)
        if with_predictions_tab:
            tab5_content = generate_prediction_tab(manager)
    else:
        tab1_content = dbc.Card(dbc.CardBody("Load an account statement (*.csv)"))
        tab2_content = dbc.Card(dbc.CardBody("Load an account statement (*.csv)"))
        tab3_content = dbc.Card(dbc.CardBody("Load an account statement (*.csv)"))
        tab4_content = dbc.Card(dbc.CardBody("Load an account statement (*.csv)"))
        if with_predictions_tab:
            tab5_content = dbc.Card(dbc.CardBody("Load an account statement (*.csv)"))

    tabs= [
        dbc.Tab(tab1_content, label="Overview"),
        dbc.Tab(tab2_content, label="Transfers"),
        dbc.Tab(tab3_content, label="Individual Transfers"),
        dbc.Tab(tab4_content, label="Dataset"),
    ]
    if with_predictions_tab:
        tabs.append(dbc.Tab(tab5_content, label="Predictions"))

    return tabs



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

    fig = make_subplots(
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
    predictor = RegularTransactionPredictor(Config())
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
budget_book = Dash(__name__, server=server, external_stylesheets=[dbc.themes.COSMO])

def uploaded_csv_to_iostream(contents, filename):
    if ".csv" not in filename:
        return

    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    iostream = io.StringIO(decoded.decode("utf-8"))
    return iostream


@budget_book.callback(
    Output("modal", "is_open"),
    Input("open-settings-button", "n_clicks"),
    State("modal", "is_open"),
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open


@budget_book.callback(
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
            df = parse_csv_files_to_dataframe(contents, filenames)
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
            df = parse_csv_files_to_dataframe(contents, filenames)
            csv_parser = AccountStatementCsvParser(
                df,
                Config(),
            )
            status_text, status_class = set_success(
                f"{len(filenames)} file(s) uploaded succesfully. Pick a time range and click on update!"
            )

            transaction_visualizer = TransactionVisualizer(Config())
            transaction_visualizer.set_transactions(csv_parser.to_dated_transactions())

            transaction_visualizer.set_analysis_interval(
                datetime.strptime(start_date, "%Y-%m-%d").date(),
                datetime.strptime(end_date, "%Y-%m-%d").date() + relativedelta(days=1),
            )
            if transaction_visualizer.dataset_is_valid():
                output_tabs = generate_tabs(transaction_visualizer, with_predictions_tab=enable_predictions)
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

def parse_csv_files_to_dataframe(contents, filenames):
    dfs = []
    for filename, content in zip(filenames, contents):
        parser = AccountStatementCsvParser(
                    uploaded_csv_to_iostream(content, filename),
                    Config(),
                )
        dfs.append(parser.get_csv_dataframe())

    df = pd.concat(dfs).drop_duplicates()
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Budget Book Webserver.")
    parser.add_argument("--from-module", type=str, default=None, help="Start server in demo mode with dummy-data.")
    parser.add_argument("--debug", action="store_true", default=False, help="Start webserver in debug mode.")
    parser.add_argument("--generate-predictions", action="store_true", default=False, help="Enable experimental predictions.")
    parser.add_argument("config", type=str, help="Path to configuration yaml file!")

    args = parser.parse_args()

    if args.generate_predictions:
        enable_predictions = True

    # Instantiate shared config once with path to config file
    Config(args.config)

    if args.from_module: 
        manager = TransactionVisualizer(config=Config())

        import importlib
        try:
            imported_module = importlib.import_module(args.from_module)
            manager.add_transactions(imported_module.build_dataset())
        except :
            raise ModuleNotFoundError(f"Provided module {args.from_module} can not be imported!")

        manager.set_analysis_interval_to_max_range()

        budget_book.layout = dbc.Container(
            [
                html.H1("Budget Book Dashboard", style={"textAlign": "center"}),
                dbc.Tabs(generate_tabs(manager, with_predictions_tab=False), id="tabs"),
            ],
            style={"width": "80vw", "minWidth": "80vw"},
        )
    else:
        budget_book.layout = dbc.Container(
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
                dbc.Tabs(generate_tabs(None, with_predictions_tab=False), id="tabs"),
            ],
            style={"width": "80vw", "minWidth": "80vw"},
        )
    budget_book.run_server(debug=args.debug)
