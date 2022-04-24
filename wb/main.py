import numpy
import pprint
import pandas as pd
import dash
from dash.dependencies import Input, Output, State

import dash_bootstrap_components as dbc
from dash import dash_table

from dash import html
from dash import dcc
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv('data/actual.csv').drop('Unnamed: 0', axis=1)
df.drop(1, axis=0, inplace=True)




##Select type of goods
options = []

for k in df['Обоснование для оплаты'].unique():
    options.append({'label': k, 'value': k})


seletTypeOfPay = dcc.Dropdown(
    id='typeOfPay',
    options= options,
    value= ['Логистика'],
    multi=True

)


tab1 = [
    dbc.Row([
        dbc.Col([html.Div(id='data-table')])
], style={'margin-top': '20px', 'margin-right': '20px'})]


app = dash.Dash(__name__,  external_stylesheets=[dbc.themes.UNITED])

app.layout = html.Div([
    dcc.Store(id='filltered-data', storage_type='memory'),

    ##body
    html.Div([
##filters
    dbc.Row([
        dbc.Col([
                html.H3('Обоснование оплаты'),
                html.Div(seletTypeOfPay)

        ], width={'size': 4, 'offset': 1}),

        dbc.Col([
            dbc.Button('Apply', id='submitVal', n_clicks=0, className='mr-2')
        ],  align='end')


            ])

    ]),

    ## tabs


    html.Div([

dbc.Tabs([dbc.Tab(tab1, label='Charts'),
          dbc.Tab(html.H4('Таблица 1'), label='Data'),
          dbc.Tab(html.H4('Таблица'), label='Tab 3')])
])

    ### tabs end
])





@app.callback(
    Output('filltered-data', 'data'),
    Input(component_id='submitVal', component_property='n_clicks'),
    [State('typeOfPay', 'value')]

)
def coockdata(n_clicks, dtval):
    sort_data = df[df['Обоснование для оплаты'].isin(dtval)]

    return sort_data.to_json(date_format='iso', orient='split', default_handler=str)



@app.callback(Output(component_id='data-table', component_property='children'), Input('filltered-data', 'data'))

def table_content(data):
    table_data = pd.read_json(data, orient='split')
    if len(table_data) == 0:
        return html.H4('Pleace Select more data')



    ##RAW DATA TABLE
    tbl1 = dash_table.DataTable(data=table_data.to_dict('records'), columns=[{'name': i, 'id': i} for i in table_data.columns],
                                style_data={'width': '50px', 'maxWidth': '100px', 'minWidth': '100px'},

                                style_header={
                                    'backgroundColor': 'rgb(37, 150, 190)',
                                    'color': 'white',
                                    'fontWeight': 'bold',
                                    'textAlign': 'center'
                                },
                                page_size=50
                                )

    html5 = [html.H4('Raw data'), tbl1]
    return html5






if __name__ == '__main__':
    app.run_server(debug=True)