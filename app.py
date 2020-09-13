import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import json
import pandas as pd
from helper import config as cfg

gulf_geojson = json.load(open('assets/iho.json'))

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
        'data': [
            go.Scattermapbox(
                lat=[45.659196],
                lon=[-66.196285],
                mode='markers',
                marker=dict(size=4)
            )
        ],
        'layout': go.Layout(autosize=True, hovermode='closest', height=900
        , mapbox = {'accesstoken': cfg.MAPBOX_TOKEN, 'bearing': 0, 'layers':
                [dict(sourcetype='geojson', source=gulf_geojson, type='fill', color = 'rgba(208,28,139,0.8)')]
                    , 'center': {'lat': 48, 'lon': -61}, 'zoom': 5
                    , 'style': 'mapbox://styles/mapbox/light-v9'
                    }
        )
    }

if __name__== '__main__':
    app.run_server(debug=True)