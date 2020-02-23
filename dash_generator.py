
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
from collections import defaultdict

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

data_file_excel = 'data.xlsx'

trade_df, instrument_df, contract_df, eod_prices_df = report.read_tables('data/data.xlsx')


available_asset = instrument_df.iloc[:, 2].unique()

available_instrument = instrument_df.iloc[:, 0]

available_contract = contract_df.iloc[:, 0]

dict_all = defaultdict(lambda: defaultdict(dict))


#add all
for i in range(len(available_asset)):
    asset_mask = (instrument_df.iloc[:, 2] == available_asset[i])
    asset_instruments = list(instrument_df.iloc[:, 1][asset_mask])
    asset_instruments_code = list(instrument_df.iloc[:, 0][asset_mask])
    all_instrument_asset = []
    for j in range(len(asset_instruments)):
        instrument_mask = (contract_df.iloc[:, 2] == asset_instruments_code[j])
        instrument_contract = list(available_contract[instrument_mask])
        all_instrument_asset = all_instrument_asset + instrument_contract

    all_instrument_asset.insert(0, 'All')
    dict_all[available_asset[i]]['All'] = all_instrument_asset


for i in range(len(available_asset)):
    asset_mask = (instrument_df.iloc[:, 2] == available_asset[i])
    asset_instruments = list(instrument_df.iloc[:, 1][asset_mask])
    asset_instruments_code = list(instrument_df.iloc[:, 0][asset_mask])
    for j in range(len(asset_instruments)):
        instrument_mask = (contract_df.iloc[:, 2] == asset_instruments_code[j])
        instrument_contract = list(available_contract[instrument_mask])
        instrument_contract.insert(0, 'All')
        dict_all[available_asset[i]][asset_instruments[j]] = instrument_contract

names = list(dict_all.keys())

print(list(dict_all['Equity'].keys()))


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
                            searchable=True
                        ),
                    ),
                    html.Div(
                        dcc.Dropdown(
                            id='contract-dropdown',
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

@app.callback(
    dash.dependencies.Output('instrument-dropdown', 'options'),
    [dash.dependencies.Input('asset-class-dropdown', 'value')]
)
def update_instrument_dropdown_options(asset_name):
    print([{'label': i, 'value': i} for i in list(dict_all[asset_name].keys())])
    return [{'label': i, 'value': i} for i in list(dict_all[asset_name].keys())]


@app.callback(
    dash.dependencies.Output('instrument-dropdown', 'value'),
    [dash.dependencies.Input('asset-class-dropdown', 'value')]
)
def update_instrument_dropdown_value(asset_name):
    return list(dict_all[asset_name].keys())[0]


@app.callback(
    dash.dependencies.Output('contract-dropdown', 'options'),
    [
        dash.dependencies.Input('asset-class-dropdown', 'value'),
        dash.dependencies.Input('instrument-dropdown', 'value')
    ]
)
def update_contract_dropdown_options(asset_name, instrument_name):
    return [{'label': i, 'value': i} for i in list(dict_all[asset_name][instrument_name])]

@app.callback(
    dash.dependencies.Output('contract-dropdown', 'value'),
    [
        dash.dependencies.Input('asset-class-dropdown', 'value'),
        dash.dependencies.Input('instrument-dropdown', 'value')
    ]
)
def update_contract_dropdown_value(asset_name, instrument_name):
    return list(dict_all[asset_name][instrument_name])[0]










if __name__ == '__main__':
    app.run_server(debug=True)