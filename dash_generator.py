import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd

app = dash.Dash()

app.layout = html.Div(children=[html.H1('Trieu Ho')])

df = pd.DataFrame(
    {
        "First Name": ["Arthur", "Ford", "Zaphod", "Trillian"],
        "Last Name": ["Dent", "Prefect", "Beeblebrox", "Astra"],
    }
)

table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)

if __name__ == '__main__':
    app.run_server(debug=True)