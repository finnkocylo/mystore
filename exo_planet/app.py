import dash


from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash import dash_table

from dash import html
from dash import dcc

import plotly.express as px
import plotly.graph_objects as go


import pandas as pd
import requests

import numpy as np



mc = pd.read_excel('report.xls')

# print(mc.head())

"""READ DATA"""


response = requests.get('http://asterank.com/api/kepler?query={}&limit=2000')
df = pd.json_normalize(response.json())
df = df[df['PER'] > 0]
df['KOI'] = df['KOI'].astype(int, errors='ignore')

# fig = px.scatter(df, x='TPLANET', y='A')

# create a star size category
bins = [0, 0.8, 1.2, 100]
names = ['small', 'similar', 'bigger']
df['StarSize'] = pd.cut(df['RSTAR'], bins=bins, labels=names)
options = []

for k in names:
    options.append({'label': k, 'value': k})


# Tempreture bins
tp_bins = [0, 200, 400, 500, 5000]
tp_labels = ['low', 'optimal', 'high', 'extreme']
df['temp'] = pd.cut(df['TPLANET'], tp_bins, labels=tp_labels)


#size bins
rp_bins = [0, 0.5, 2, 4, 100]
rp_labels = ['low', 'optimal', 'high', 'extreme']
df['gravity'] = pd.cut(df['RPLANET'], rp_bins, labels=rp_labels)


# estimate an object status
df['status'] = np.where((df['temp'] == 'optimal') & (df['gravity'] == 'optimal'), 'promising', None)
df.loc[:, 'status'] = np.where((df['temp'] == 'optimal') & (df['gravity'].isin(['low', 'high'])), 'challenging', df['status'])
df.loc[:, 'status'] = np.where((df['gravity'] == 'optimal') & (df['temp'].isin(['low', 'high'])), 'challenging', df['status'])
df['status'] = df.status.fillna('extreme')


#Relative distance. Distance to SUN/SUM redi

df.loc[:, 'relative_dist'] = df['A'] / df['RSTAR']


# Design settings
CHARTS_TEMPLATE = go.layout.Template(

    layout = dict(
        font=dict(family='Century Gothic', size=14),
        legend = dict(orientation='h', title_text='', x=0, y=1.1)
    )
)

COLOR_STATUS_VALUES = ['#e9f5f9', '#145369', '#49be25']



# print(df.groupby('status')['ROW'].count())

### selector category size
star_size_selector = dcc.Dropdown(
    id='star_selector',
    options=options, 
    value = ['small', 'similar', 'bigger'],
    multi=True
)


rplanet_selector = dcc.RangeSlider(
    id='range_slider',
    min = min(df['RPLANET']),
    max = max(df['RPLANET']),
    marks = {5: '5', 10: '10', 15:'15', 20:'20'},
    step=1,
    value=[min(df['RPLANET']), max(df['RPLANET'])]

)

# TABS content

tab1_content = [
#charts
    dbc.Row([
        dbc.Col(html.Div(id='dist-temp-chart'), md=6),
        dbc.Col(html.Div(id='colestial-chart'), md=6)
    ], style={'margin-bottom': '40px', 'margin-top': '20px'}),

    dbc.Row([
        dbc.Col(html.Div(id='relative-dist-chart'), md=6),
        dbc.Col(html.Div(id='mstar-tstar-chart'), md=6)

    ])


]

tab2_content = [ dbc.Row(html.Div(id='data-table'), style={'margin-bottom': '40px', 'margin-top': '20px'})]

#tab 3 content


table_header = [html.Thead(html.Tr([html.Th("Field Name"), html.Th("Details")]))]
expl = { 'KOI':'Object of Interest number',
'A':'Semi-major axis (AU)',
'RPLANET':'Planetary radius (Earth radii)',
'RSTAR':'Stellar radius (Sol radii)',
'TSTAR':'Effective temperature of host star as reported in KIC (k)',
'KMAG':'Kepler magnitude (kmag)',
'TPLANET':'Equilibrium temperature of planet, per Borucki et al. (k)',
'T0':'Time of transit center (BJD-2454900)',
'UT0':'Uncertainty in time of transit center (+-jd)',
'UT0':'Uncertainty in time of transit center (+-jd)',
'PER':'Period (days)',
'UPER':'Uncertainty in period (+-days)',
'DEC':'Declination (@J200)',
'RA':'Right ascension (@J200)',
'MSTAR':'Derived stellar mass (msol)'}

tbl_rows = []
for i in expl:
    tbl_rows.append(html.Tr([html.Td(i), html.Td(expl[i])]))

table_body = [html.Tbody(tbl_rows)]
table = dbc.Table(table_header + table_body, bordered=True)





text = 'Data are sourced from Kelper API via asterank.com'
tab3_content = [dbc.Row(html.A(text, href='http://www.asterank.com/kepler'), style={'margin-top': '20px'}),
                dbc.Row(html.Div(children=table), style={'margin-top': '20px', 'width': '50%'})]





"""LAYOUT"""


app = dash.Dash(__name__,  external_stylesheets=[dbc.themes.LUMEN])

app.layout = html.Div([
    # header

    dbc.Row([
            dbc.Col(html.Img(src=app.get_asset_url('images/exo.jpg'), style={'width': '130px', 'marginLeft': '40px'}), md=1),
            dbc.Col([
                    html.H1('Exoplanet Data Visualisation'),
                    html.A('Read about exoplanet', href='https://spaceplace.nasa.gov/menu/earth/')], md=7),
            dbc.Col(html.Div([
                html.P('Developed by'),
                html.A('Dmitry Kotsilo', href='', style={'marginLeft': '2px'})], className='app-referral'), md=4)], className='app-header'),




    dcc.Store(id='filtered-data', storage_type='session'),

    #body
    html.Div([

    #filters
    #slider filter: by radius of planet
    dbc.Row([
        dbc.Col([
            html.H4('Select planet major semi-axis', style={'marginTop': '23px'}),
            html.Div(rplanet_selector)
        ], width={'size': 3}),

    #dropdown menu by size of planet
        dbc.Col([
            html.H4('Star size'),
            html.H4(star_size_selector)

        ], width={'size': 3, 'offset': 1}),

        dbc.Col(dbc.Button('Apply', id='submit-val', n_clicks=0, class_name='mr-2'), style={'margin-top': '35px'})


    ], style={'margin-bottom': '40px'}),

    #charts
    dbc.Tabs([
        dbc.Tab(tab1_content, label='Charts'),
        dbc.Tab(tab2_content, label='Data'),
        dbc.Tab(tab3_content, label='About'),
    ])
    # dbc.Row([
    #     dbc.Col(html.Div(id='dist-temp-chart'), md=6),
    #     dbc.Col(html.Div(id='colestial-chart'), md=6)
    # ], style={'margin-bottom': '40px'}),
    #
    # dbc.Row([
    #     dbc.Col(html.Div(id='relative-dist-chart'), md=6),
    #     dbc.Col(html.Div(id='mstar-tstar-chart'), md=6)
    #
    # ])
], className='app-body')])




"""CALLBACKS"""


@app.callback(
    Output(component_id='filtered-data', component_property='data'),
    [Input(component_id='submit-val', component_property='n_clicks')],
    [State(component_id='range_slider', component_property='value'),
    State(component_id='star_selector', component_property='value')])


def filter_data(n, radius_range, star_size):
    my_data = df[(df['RPLANET'] > radius_range[0]) &
        (df['RPLANET'] < radius_range[1]) &
        (df['StarSize'].isin(star_size))]

    return my_data.to_json(date_format='iso', orient='split', default_handler=str)




@app.callback(
    Output(component_id='colestial-chart', component_property='children'),
    Input(component_id='filtered-data', component_property='data')
)
def colestial_chart(data):
     chart_data = pd.read_json(data, orient='split')

     if len(chart_data) == 0:
         return html.Div('Please select more data')


     fig = px.scatter(chart_data, x='RA', y='DEC', size='RPLANET', color='status', color_discrete_sequence=COLOR_STATUS_VALUES)
     fig.update_layout(template=CHARTS_TEMPLATE)
     html1 = html.H3('Position on the Colestial Shere'), dcc.Graph(figure=fig)

     return html1




@app.callback(
    Output(component_id='dist-temp-chart', component_property='children'),
    Input(component_id='filtered-data', component_property='data')
)
def dist_temp_сhart(data):
     chart_data = pd.read_json(data, orient='split')

     if len(chart_data) == 0:
         return html.Div('Please select more data')

     fig = px.scatter(chart_data, x='TPLANET', y='A', color='StarSize')
     fig.update_layout(template=CHARTS_TEMPLATE)
     html2 = html.H3('Planet Tempriature  - Distance from the star'), dcc.Graph(figure=fig)


     return html2







@app.callback(
    [
    Output(component_id='relative-dist-chart', component_property='children'),
    Output(component_id='mstar-tstar-chart', component_property='children'),
     Output(component_id='data-table', component_property='children')],
    [Input(component_id='filtered-data', component_property='data')]

)

def update_chart(data):

    chart_data = pd.read_json(data, orient='split')

    if len(chart_data) == 0:
        return html.Div(), html.Div('Please select more data'), html.Div(), html.Div()
    # Star size  ~ Planet temp chart
    # fig1 = px.scatter(chart_data, x='TPLANET', y='A', color='StarSize')
    # fig1.update_layout(template=CHARTS_TEMPLATE)
    # html1 =  [html.H3('Planet Tempriature  - Distance from the star'), dcc.Graph(figure=fig1)]

    #Celestial coord chart
    # fig2 = px.scatter(chart_data, x='RA', y='DEC', size='RPLANET', color='status', color_discrete_sequence=COLOR_STATUS_VALUES)
    # fig2.update_layout(template=CHARTS_TEMPLATE)
    # html2 = [html.H3('Position on the Colestial Shere'), dcc.Graph(figure=fig2)]

    #Relative dist chart
    fig3 = px.histogram(chart_data, x="relative_dist", color='status', barmode='overlay', marginal='violin')
    fig3.update_layout(template=CHARTS_TEMPLATE)
    fig3.add_vline(x=1, y0=0, y1=160,  annotation_text='Earth', line_dash="dot")
    html3 = [html.H3('Relative Distance (AU/Sol radii)'), dcc.Graph(figure=fig3)]

    fig4 = px.scatter(chart_data, x='MSTAR', y='TSTAR', size='RPLANET', color='status', color_discrete_sequence=COLOR_STATUS_VALUES)
    fig4.update_layout(template=CHARTS_TEMPLATE)
    html4 = [html.H3('Star Mass ~ Star tempriature'), dcc.Graph(figure=fig4)]

    #Raw data table
    raw_data = chart_data.drop(['relative_dist', 'StarSize', 'ROW', 'temp', 'gravity'], axis=1)
    tb1 = dash_table.DataTable(data=raw_data.to_dict('records'), columns=[{'name': i, 'id': i}
        for i in raw_data.columns],
        style_data={'width': '100px', 'maxWidth': '100px', 'minWidth': '100px'},
        style_header={'textAlign': 'center', 'backgroundColor': '#bbb'},
        page_size=30
        )

    html5 = [html.H3('Raw data'), tb1]


    return html3, html4, html5







if __name__ == '__main__':
    app.run_server(debug=True)





# @app.callback(
#     Output(component_id='dist-temp-chart', component_property='figure'),
#     [Input(component_id='range_slider', component_property='value'),
#         Input(component_id='star_selector', component_property='value')]
# )
#
# def update_dist_temp_chart(radius_range, star_size):
#     chart_data = df[(df['RPLANET'] > radius_range[0]) &
#         (df['RPLANET'] < radius_range[1]) &
#         (df['StarSize'].isin(star_size))]
#
#     fig = px.scatter(chart_data, x='TPLANET', y='A', color='StarSize')
#
#     return fig


# Callback for colestial shere
