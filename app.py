import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import json
# from helper import db
import pandas as pd
from helper import config as cfg

gulf_geojson = json.load(open('assets/iho.json'))
# fish_data = db.run_query()
fish_data = pd.read_csv('test.csv') # dummy query to avoid hitting up RDS for testing

def build_fish_dropdown():
    not_fish = ['date', 'station', 'longitude', 'latitude', 'depth']
    dropdown_labels = [{'label': i, 'value': i} for i in fish_data.columns if i not in not_fish]
    return dropdown_labels

# Note that static assets such as html and the like must be served from the asset folders because Dash is pain
app = dash.Dash(__name__)
app.title = 'Ocean Temperature and Salinity in the Estuary and Gulf of St. Lawrence'
server = app.server

# Serve layout separately in order for page to always load this layout on default
def serve_layout():
    fish_name = build_fish_dropdown()
    return html.Div(children=[
        html.Div([html.H2("Estuary and Gulf of St. Lawrence: Temperatures, Salinity, and Fish Populations")],
                 id='title', title='atitle')
        , html.Div(children=[html.Div(children=[html.H4('Options'),
                                                dcc.Dropdown(id='fish_dropdown', options=fish_name, value='sand_lances'),
                                                html.H4('Factors'),
                                                dcc.Dropdown(id='factor_dropdown', options=[{'label': 'Temperature', 'value': 0}, {'label': 'Salinity', 'value': 1}])
                                                ]
                                      , className='two columns')])
        , html.Div(children=[dcc.Graph(id='fish',config={'autosizable': True, 'displaylogo': False, 'displayModeBar': False}
                             , style={'width': '100%'}),
                             html.Div(dcc.RangeSlider(min=2009, max=2019, step=1, value=[2009, 2019], dots=True,
                                             marks={i: str(i) for i in range(2009, 2020)}),
                                      style={'marginBottom': 25, 'marginTop': 25})
                             ],  className='ten columns')
        , html.Div(children=[
            html.Div(html.H2(), className='two columns'),
            html.Div(className='ten columns')])
        , html.Iframe(id='map', src=app.get_asset_url('test.html'), width='100%', height='600')
])
app.layout = serve_layout


# this is a simple callback function for when the fish dropdown changes - you serve data to the input
# and output. only 1 input can serve a change, but can serve to multiple outputs.
@app.callback(
    dash.dependencies.Output('fish', 'figure')
    , [dash.dependencies.Input('fish_dropdown', 'value')]
)
def update_figure(selected):
    print(selected)
    return {
        'data': [
            go.Scattermapbox(
                lat=fish_data[fish_data[selected]>0]['latitude'].tolist(),
                lon=fish_data[fish_data[selected]>0]['longitude'].tolist(),
                mode='markers',
                marker=dict(size=4)
            )
        ],
        'layout': go.Layout(autosize=True, hovermode='closest', height=600
                            , margin=dict(l=0, r=0, b=0, t=0, pad=0)
                            , mapbox = {'accesstoken': cfg.MAPBOX_TOKEN, 'bearing': 0, 'layers':
                [dict(sourcetype='geojson', source=gulf_geojson, type='fill', color = 'rgba(208,28,139,0.8)')]
                    , 'center': {'lat': 48.3, 'lon': -64.5}, 'zoom': 5
                    , 'style': 'mapbox://styles/mapbox/light-v9'
                    }
        )
    }




if __name__== '__main__':
    app.run_server(debug=True)