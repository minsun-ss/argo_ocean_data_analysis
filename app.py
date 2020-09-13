import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import json
import pandas as pd

df_html = pd.read_csv('data/test.csv').to_html()

app = dash.Dash(__name__)
app.title = 'Ocean Temperature and Salinity in the Estuary and Gulf of St. Lawrence'
server = app.server

app.layout = html.Div([
    html.H1("Some Stuff")
    #, html.Iframe(id='map', src=open('data/test.html').read(), width='100%', height='600')
])

if __name__== '__main__':
    app.run_server(debug=True)