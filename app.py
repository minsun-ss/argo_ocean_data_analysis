import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import json
import pandas as pd
from helper import config as cfg

# Note that static assets such as html and the like must be served from the asset folders because Dash is pain
app = dash.Dash(__name__)
app.title = 'Ocean Temperature and Salinity in the Estuary and Gulf of St. Lawrence'
server = app.server

app.layout = html.Div([
    html.Div([html.H1("Some Stuff")], id='title', title='atitle')
    , html.Iframe(id='map', src=app.get_asset_url('test.html'), width='100%', height='300')
    , html.Div(dcc.Graph(id='fish'))
])

@app.callback(
    dash.dependencies.Output('fish', 'figure')
    , [dash.dependencies.Input('title', 'title')]
)
def update_figure(selected):
    return {
        'layout': go.Layout(autosize=True, hovermode='closest', height=600)
    }

if __name__== '__main__':
    app.run_server(debug=True)