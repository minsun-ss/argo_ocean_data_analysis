import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import json
# from helper import db
import pandas as pd
from helper import config as cfg
from pandas.api.types import CategoricalDtype

gulf_geojson = json.load(open('assets/iho.json'))
# fish_data = db.run_query()
fish_data = pd.read_csv('test.csv') # dummy query to avoid hitting up RDS for testing
fish_data.date = pd.to_datetime(fish_data.date).dt.year # will need to import date as year
param_data = pd.read_csv('sample_param_data.csv') # same as above, code in jupyter notebook - will add it to this file later.

def build_fish_dropdown():
    not_fish = ['date', 'station', 'longitude', 'latitude', 'depth']
    dropdown_labels = [{'label': i, 'value': i} for i in fish_data.columns if i not in not_fish]
    return dropdown_labels

def build_param_dropdown():
    not_param = ['Unnamed: 0', 'year', 'depth_range']
    dropdown_labels = [{'label': i, 'value': i} for i in param_data.columns if i not in not_param]
    return dropdown_labels

def build_depth_dropdown():
    dropdown_labels = [{'label': i, 'value': i} for i in sorted([i for i in param_data.depth_range.unique()])]
    return dropdown_labels

# Note that static assets such as html and the like must be served from the asset folders because Dash is pain
app = dash.Dash(__name__)
app.title = 'Ocean Temperature and Salinity in the Estuary and Gulf of St. Lawrence'
server = app.server

# Serve layout separately in order for page to always load this layout on default
def serve_layout():
    fish_name = build_fish_dropdown()
    param_name = build_param_dropdown()
    depth_interval = build_depth_dropdown()

    return html.Div(children=[
        html.Div([html.H2("Estuary and Gulf of St. Lawrence: Temperatures, Salinity, and Fish Populations")],
                 id='title', title='atitle')
        , html.Div(children=[html.Div(children=[html.H4('Options'),
                                                dcc.Dropdown(id='fish_dropdown', options=fish_name, value='sand_lances'),
                                                html.H4('Parameter'),
                                                dcc.Dropdown(id='param_dropdown', options=param_name, value='temperature'),
                                                html.H4('Depth'),
                                                dcc.Dropdown(id='depth_dropdown', options=depth_interval, value='(0, 100]')
                                                ]
                                      , className='two columns')])
        , html.Div(children=[dcc.Graph(id='fish',config={'autosizable': True, 'displaylogo': False, 'displayModeBar': False}
                             , style={'width': '100%'}),
                             ],  className='ten columns')
        , html.Div(children=[dcc.Slider(id='year-slider', min=fish_data.date.min(),
            max=fish_data.date.max(),
            value=fish_data.date.min(),
            marks={str(year): str(year) for year in fish_data.date.unique()},
            step=None)], style={'marginBottom': 25, 'marginTop': 25, 'width':'90%'}, className='ten columns')
        , html.Div(children=[
            html.Div(html.H2(), className='two columns'),
            html.Div(className='ten columns')])
        #, html.Iframe(id='map', src=app.get_asset_url('test.html'), width='100%', height='600')
])
app.layout = serve_layout
# app.config['suppress_callback_exceptions'] = True


# this is a simple callback function for when the dropdowns changes - you serve data to the input
# and output. only 1 input can serve a change, but can serve to multiple outputs.
@app.callback(
    dash.dependencies.Output('fish', 'figure')
    , [dash.dependencies.Input('fish_dropdown', 'value'),
       dash.dependencies.Input('param_dropdown', 'value'),
       dash.dependencies.Input('depth_dropdown', 'value'),
       dash.dependencies.Input('year-slider', 'value')
       ])

def update_figure(fish_value, param_value, depth_value, year_value):
    print(fish_value, param_value, depth_value, year_value)

    color_value = param_data[(param_data.depth_range == depth_value)&(param_data.year == year_value)][param_value].item()
    print(color_value)
    if param_value not in ['temperature', 'salinity']:
        b_value = (color_value+5)/8*255
    elif param_value == 'temperature':
        b_value = (color_value-3)/8*255
    elif param_value == 'salinity':
        b_value = (color_value-30)/6*255
    else:
        b_value = 0
    # Should always be in the RGB range 0-255
    b_value = max(b_value, 0)
    b_value = min(b_value, 255)
    col = f'rgb({b_value}, {b_value}, 255)'
    print(col)

    return {
        'data': [
            go.Densitymapbox(
                lat=fish_data[(fish_data[fish_value] > 0) & (fish_data.date == year_value)]['latitude'].tolist(),
                lon=fish_data[(fish_data[fish_value] > 0) & (fish_data.date == year_value)]['longitude'].tolist(),
                radius=10
            )
        ],

        'layout': go.Layout(autosize=True, hovermode='closest', height=600
                            , margin=dict(l=0, r=0, b=0, t=0, pad=0)
                            , mapbox = {'accesstoken': cfg.MAPBOX_TOKEN, 'bearing': 0, 'layers':
                [dict(sourcetype='geojson', source=gulf_geojson, type='fill', color=col)]
                    , 'center': {'lat': 48.3, 'lon': -64.5}, 'zoom': 5
                    , 'style': 'mapbox://styles/mapbox/light-v9'
                    }
        )
    }


if __name__== '__main__':
    app.run_server(debug=True)