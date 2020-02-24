import report_generator as report
from datetime import datetime as dt
import dash
import dash_html_components as html
import dash_core_components as dcc
from collections import defaultdict
import dash_table
import pandas as pd
import plotly.express as px


pd.set_option('precision', 2)

data_file_excel = 'data/data.xlsx'

trade_df, instrument_df, contract_df, eod_prices_df = report.ReportAnalytics.read_tables(data_file_excel)

available_asset = instrument_df.iloc[:, 2].unique()

available_instrument = instrument_df.iloc[:, 0]

available_contract = contract_df.iloc[:, 0]

column_names = report.ReportAnalytics(data_file_excel, 'CCN9 Comdty', '2019-04-30', '2019-05-30').ticker_summary.columns


dict_all = defaultdict(lambda: defaultdict(dict))


# add all
for i in range(len(available_asset)):
    asset_mask = (instrument_df.iloc[:, 2] == available_asset[i])
    asset_instruments = list(instrument_df.iloc[:, 1][asset_mask])
    asset_instruments_code = list(instrument_df.iloc[:, 0][asset_mask])
    all_instrument_asset = []
    for j in range(len(asset_instruments)):
        instrument_mask = (contract_df.iloc[:, 2] == asset_instruments_code[j])
        instrument_contract = list(available_contract[instrument_mask])
        all_instrument_asset = all_instrument_asset + instrument_contract

    all_instrument_asset.insert(0, "All")
    dict_all[available_asset[i]]['All'] = all_instrument_asset


for i in range(len(available_asset)):
    asset_mask = (instrument_df.iloc[:, 2] == available_asset[i])
    asset_instruments = list(instrument_df.iloc[:, 1][asset_mask])
    asset_instruments_code = list(instrument_df.iloc[:, 0][asset_mask])
    for j in range(len(asset_instruments)):
        instrument_mask = (contract_df.iloc[:, 2] == asset_instruments_code[j])
        instrument_contract = list(available_contract[instrument_mask])
        instrument_contract.insert(0, "All")
        dict_all[available_asset[i]][asset_instruments[j]] = instrument_contract

names = list(dict_all.keys())

app = dash.Dash(__name__, assets_url_path='assets')

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
                                className="logo", src=app.get_asset_url('logo_fixed.png')
                            ),
                            html.H6(className="title-header", children="Table Filters"),
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
                        initial_visible_month=dt(2019, 4, 30),
                        end_date=dt(2019, 5, 7),
                        start_date=dt(2019, 4, 30)
                    ),
                    html.Hr(),
                    html.Div(
                        className="div-info",
                        children=[
                            html.H6(className="title-header", children="Graph Display"),
                        ],
                    ),
                    html.Div(
                        dcc.Dropdown(
                            id='graph-dropdown',
                            options=[{'label': name, 'value': name} for name in column_names[1:]],
                            value=column_names[1],
                            searchable=True
                        ),
                    ),
                ]
            ),
            html.Div(
                className="four columns div-right-panel",
                children=[
                    html.H3(
                        "Trade Summary Report",
                        style={"margin-bottom": "0px"},
                    ),
                    dash_table.DataTable(
                        id='summary-table',
                        columns=[{"name": i, "id": i} for i in column_names],
                        style_cell={
                            # all three widths are needed
                            'minWidth': '90px', 'width': '90px', 'maxWidth': '120px',
                            'overflow': 'hidden',
                        },
                        style_table={
                            'maxHeight': '210px',
                            'overflowY': 'scroll',
                            'border':'thin lightgrey solid'
                        },
                    ),
                    dcc.Graph(
                        id='summary-graph'
                    ),
                ], style={"height": "30%", "width": "50%"},
            ),
        ]
)


# display graph based on selection
@app.callback(
    dash.dependencies.Output('summary-graph', 'figure'),
    [
        dash.dependencies.Input('asset-class-dropdown', 'value'),
        dash.dependencies.Input('instrument-dropdown', 'value'),
        dash.dependencies.Input('contract-dropdown', 'value'),
        dash.dependencies.Input('my-date-picker-range', 'start_date'),
        dash.dependencies.Input('my-date-picker-range', 'end_date'),
        dash.dependencies.Input('graph-dropdown', 'value')
    ]
)
def update_graph(asset_name, instrument_name, contract_name, start_date, end_date, graph_option):
    if start_date < end_date:
        if graph_option is not None:
            pnl_obj_sum = report.summary_total(data_file_excel, contract_name,
                                               instrument_name, asset_name, start_date, end_date)
            x_name = pnl_obj_sum.columns[0]
            y_name = graph_option
            fig = px.line(pnl_obj_sum, x=x_name, y=y_name, template='plotly_white')

            return fig


# instrument dropdown options
@app.callback(
    dash.dependencies.Output('instrument-dropdown', 'options'),
    [dash.dependencies.Input('asset-class-dropdown', 'value')]
)
def update_instrument_dropdown_options(asset_name):
    return [{'label': i, 'value': i} for i in list(dict_all[asset_name].keys())]


# instrument dropdown value
@app.callback(
    dash.dependencies.Output('instrument-dropdown', 'value'),
    [dash.dependencies.Input('asset-class-dropdown', 'value')]
)
def update_instrument_dropdown_value(asset_name):
    return list(dict_all[asset_name].keys())[0]


# contract dropdown options
@app.callback(
    dash.dependencies.Output('contract-dropdown', 'options'),
    [
        dash.dependencies.Input('asset-class-dropdown', 'value'),
        dash.dependencies.Input('instrument-dropdown', 'value')
    ]
)
def update_contract_dropdown_options(asset_name, instrument_name):
    return [{'label': i, 'value': i} for i in list(dict_all[asset_name][instrument_name])]


# contract dropdown value
@app.callback(
    dash.dependencies.Output('contract-dropdown', 'value'),
    [
        dash.dependencies.Input('asset-class-dropdown', 'value'),
        dash.dependencies.Input('instrument-dropdown', 'value')
    ]
)
def update_contract_dropdown_value(asset_name, instrument_name):
    return list(dict_all[asset_name][instrument_name])[0]


# display table based on selection
@app.callback(
    dash.dependencies.Output('summary-table', 'data'),
    [
        dash.dependencies.Input('asset-class-dropdown', 'value'),
        dash.dependencies.Input('instrument-dropdown', 'value'),
        dash.dependencies.Input('contract-dropdown', 'value'),
        dash.dependencies.Input('my-date-picker-range', 'start_date'),
        dash.dependencies.Input('my-date-picker-range', 'end_date'),
    ]
)
def update_summary_table(asset_name, instrument_name, contract_name, start_date, end_date):
    if start_date < end_date:
        pnl_obj_sum = report.summary_total(data_file_excel, contract_name,
                                           instrument_name, asset_name, start_date, end_date)
        pnl_obj_sum.iloc[:,3] = pnl_obj_sum.iloc[:,3].map("{:,.2f}".format)
        pnl_obj_sum.iloc[:,4] = pnl_obj_sum.iloc[:,4].map("{:,.2f}".format)
        pnl_obj_sum.iloc[:,5] = pnl_obj_sum.iloc[:,5].map("{:,.2f}".format)
        final_df = pnl_obj_sum.to_dict('records')
        return final_df


if __name__ == '__main__':
    app.run_server(debug=True)
