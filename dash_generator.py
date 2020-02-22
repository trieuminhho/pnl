
import os
import pathlib
import statistics
from collections import OrderedDict

import pathlib as pl
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output, State
import report_generator as report
import utils

from datetime import datetime as dt
import dash
import dash_html_components as html
import dash_core_components as dcc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

data_file_excel = 'data.xlsx'

trade_df, instrument_df, contract_df, eod_prices_df = report.read_tables('data/data.xlsx')


available_tickers = contract_df.iloc[:, 0].unique()

print(available_tickers)


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Dash App Layout
app.layout = html.Div(
        className="row",
        children=[
            html.Div(
                className="three columns div-left-panel",
                children=[
                    # Div for Left Panel App Info
                    html.Div(
                        className="div-info",
                        children=[
                            html.Img(
                                className="logo", src=app.get_asset_url("dash-logo-new.png")
                            ),
                            html.H6(className="title-header", children="Trade Report"),
                        ],
                    ),
                    html.Div(
                        dcc.Dropdown(
                            className="div-dropdown",
                            options=[
                                {'label': 'New York City', 'value': 'NYC'},
                                {'label': 'Montreal', 'value': 'MTL'},
                                {'label': 'San Francisco', 'value': 'SF'}
                            ],
                            searchable=False
                        ),
                    ),
                    dcc.DatePickerRange(
                        id='my-date-picker-range',
                        min_date_allowed=dt(2000, 1, 1),
                        max_date_allowed=dt(2030, 1, 1),
                        initial_visible_month=dt(2020, 1, 1),
                    ),
                    html.Div(id='output-container-date-picker-range')
                ]
            )
        ]
)


@app.callback(
    dash.dependencies.Output('output-container-date-picker-range', 'children'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date')])
def update_output(start_date, end_date):
    string_prefix = 'You have selected: '
    if start_date is not None:
        start_date = dt.strptime(start_date.split(' ')[0], '%Y-%m-%d')
        start_date_string = start_date.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
    if end_date is not None:
        end_date = dt.strptime(end_date.split(' ')[0], '%Y-%m-%d')
        end_date_string = end_date.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'End Date: ' + end_date_string
    if len(string_prefix) == len('You have selected: '):
        return 'Select a date to see it displayed here'
    else:
        return string_prefix


if __name__ == '__main__':
    app.run_server(debug=True)