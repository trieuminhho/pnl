
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


available_asset = instrument_df.iloc[:, 2].unique()

available_instrument = instrument_df.iloc[:, 0]

asset_instrument_dict = {}

for i in range(len(available_asset)):
    asset_mask = (instrument_df.iloc[:, 2] == available_asset[i])
    asset_instruments = list(instrument_df.iloc[:, 1][asset_mask])
    asset_instruments.insert(0, 'All')
    asset_instrument_dict[available_asset[i]] = asset_instruments

available_contract = contract_df.iloc[:, 0]
instrument_contract_dict = {}

for i in range(len(available_instrument)):
    instrument_mask = (contract_df.iloc[:, 2] == available_instrument[i])
    instrument_contract = list(available_contract[instrument_mask])
    instrument_contract.insert(0, 'All')
    instrument_contract_dict[instrument_df.iloc[i, 1]] = instrument_contract


names = list(asset_instrument_dict.keys())
names2 = list(instrument_contract_dict.keys())
names3 = list(available_contract)


print(names)
print(names2)
print(names3)

print(asset_instrument_dict)
print(instrument_contract_dict)






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
                            id='asset-class-dropdown',
                            options=[{'label': name, 'value': name} for name in names],
                            value=names[0],
                            searchable=True
                        ),
                    ),
                    html.Div(
                        dcc.Dropdown(
                            id='instrument-dropdown',
                            value=names2[0],
                            searchable=True
                        ),
                    ),
                    html.Div(
                        dcc.Dropdown(
                            id='contract-dropdown',
                            value=names3[0],
                            searchable=True
                        ),
                    ),
                    html.Hr(),
                    html.Div(id='display-selected-values'),

                    dcc.DatePickerRange(
                        id='my-date-picker-range',
                        min_date_allowed=dt(2000, 1, 1),
                        max_date_allowed=dt(2030, 1, 1),
                        initial_visible_month=dt(2020, 2, 1),
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
def update_date(start_date, end_date):
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

@app.callback([
    dash.dependencies.Output('instrument-dropdown', 'options')],
    [dash.dependencies.Input('asset-class-dropdown', 'value')]
)
def update_instrument_dropdown(asset_name):
    return [{'label': i, 'value': i} for i in asset_instrument_dict[asset_name]]


@app.callback(
    [
        dash.dependencies.Output('contract-dropdown', 'options')
    ],
    [
        dash.dependencies.Input('instrument-dropdown', 'value'),
        dash.dependencies.Input('asset-class-dropdown', 'value')
    ]
)
def update_contract_dropdown(instrument_name, asset_name):
    print(instrument_name)
    if instrument_name == 'All':
        all_instruments_in_asset = []
        for key in asset_instrument_dict[asset_name][1:]:
            all_instruments_in_asset = all_instruments_in_asset + instrument_contract_dict[key][1:]

            print(all_instruments_in_asset)
            print(instrument_contract_dict[instrument_name])

        return [{'label': i, 'value': i} for i in all_instruments_in_asset]
    else:
        return [{'label': i, 'value': i} for i in instrument_contract_dict[instrument_name]]



if __name__ == '__main__':
    app.run_server(debug=True)