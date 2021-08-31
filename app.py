import time
import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import pandas_datareader.data as web
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.express as px
from copy import copy
from scipy import stats
import matplotlib.pyplot as plt
import numpy as np
import utils
import animationpyplot
import seaborn as sb


figcor = px.imshow(utils.returnarscorr)
figcor.update_layout(plot_bgcolor="lightblue",paper_bgcolor="lightblue")




app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], prevent_initial_callbacks=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )


app.layout = dbc.Container([
    dbc.Row([
         dbc.Col(html.H1("Yahoo Finance - Dash",
                        className='text-center text-primary, mb4'), style={"color": "rgb(28, 72, 119)", "text-align": "center", "background-color": "rgb(135, 186, 241)",
                        "border-top-style": "groove", "border-bottom-style": "groove"},
                width=12)
    ]),

    dbc.Row([
        dbc.Col([
            html.Div(children='''
                Normalized ADR price evolution. Select tickers:
            ''', className='graphdescription'),
            dcc.Dropdown(id='my-dpdn2', multi=True, value=['GGAL', 'YPFD'], options=[{'label': x, 'value': x}
                                                                                  for x in utils.priceusnorm.columns.tolist()]),
            dcc.Graph(id='line-fig2')
        ], width={'size': 6, 'order': 1}),

        dbc.Col([
            html.Div(children='''
        Daily ARS ADR return distribution. Select tickers
    ''', className='graphdescription'),
            dcc.Dropdown(id='my-dpdn3', multi=True, value=['GGAL', 'YPFD'],
                         options=[{'label': x, 'value': x}
                                  for x in utils.priceus.columns.tolist()]),
            dcc.Graph(id='line-fig3', figure={})],width={'size': 6, 'order': 1})

    ]),

    dbc.Row([
        dbc.Col([
            html.Div(children='''
        Correlation map between Merval tickers:
    ''', className='graphdescription'),
           dcc.Graph(id='cormap', figure=figcor)
        ], width={'size': 3, 'order': 1}),
        dbc.Col([
            html.Div(children='''
        Animation summary:
    ''', className='graphdescription'),
            html.Div(children='''
        At the right, you could appreciate the evolution of the cumulative returtn (y) and deviation (x) from 2019 until today, comparing the tickers of BRA & ARG.
    ''', className='textanimation'),
        ], width={'size': 3, 'order': 2}),

        dbc.Col([
            html.Div(children='''
        ARS & BRA ADR's scatter evolution
    ''', className='graphdescription'),
            dcc.Graph(id='line-fig4', figure=animationpyplot.animarsbra)
        ], width={'size': 6, 'order': 3})

    ], justify='around')

], fluid=True)


@ app.callback(
    Output(component_id='line-fig2', component_property='figure'),
    Input(component_id='my-dpdn2', component_property='value')
)

def update_graph_scatter(option_slctd):
    print(option_slctd)
    print(type(option_slctd))

    priceusnormdash=utils.priceusnorm.copy()
    priceusnormdash=priceusnormdash[option_slctd]
    priceusnormdash['Date']=utils.priceusnorm['Date']

    fig=go.Figure()

    for ticker in option_slctd:
        fig.add_trace(go.Scatter(x=priceusnormdash['Date'], y=priceusnormdash[ticker],
                                mode='lines', name=ticker))
        fig.update_layout(legend_bgcolor="lightblue", legend_bordercolor="blue", legend_borderwidth=1,paper_bgcolor="lightblue",plot_bgcolor="white")

    return fig

@ app.callback(
    Output(component_id='line-fig3', component_property='figure'),
    [Input(component_id='my-dpdn3', component_property='value')]
)

def update_graph_scatter(option_slctd):
    print(option_slctd)
    print(type(option_slctd))

    dfreturnus=utils.returnus.copy()
    dfreturnus=dfreturnus[option_slctd]


    fig=go.Figure()

    for ticker in option_slctd:
        fig.add_trace(go.Histogram(x=dfreturnus[ticker], name=ticker))
        fig.update_layout(barmode='stack')
        fig.update_layout(legend_bgcolor="lightblue", legend_bordercolor="blue", legend_borderwidth=1,paper_bgcolor="lightblue",plot_bgcolor="white")

    return fig

server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
