import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import json
from helper import db
import pandas as pd
from helper import config as cfg
from pandas.api.types import CategoricalDtype
import generate_data as gd

# DATA GENERATION
gulf_geojson = json.load(open('assets/iho.json'))
param_data = gd.get_param_data()
fish_aggregate = gd.get_fish_aggregate()
fish_locations = gd.get_fish_locations()
correlation_table = gd.correlation_table(fish_aggregate, param_data)

def build_dropdowns():
    fish_list = fish_aggregate['fish_type'].unique().tolist()
    fish_dropdown_labels = [{'label': i.replace('_', ' '), 'value': i} for i in fish_list]
    param_dropdown_labels = [{'label': i, 'value': i} for i in ['temperature', 'salinity']]
    depth_dropdown_labels = [{'label': i, 'value': i} for i in sorted([i for i in param_data.depth_range.unique()])]
    return fish_dropdown_labels, param_dropdown_labels, depth_dropdown_labels

# efficiencies - generate this once so we never have to generate again
FISH_DROPDOWN, PARAM_DROPDOWN, DEPTH_DROPDOWN = build_dropdowns()

# Note that static assets such as html and the like must be served from the asset folders because Dash is pain
app = dash.Dash(__name__)
app.title = 'Ocean Temperature and Salinity in the Estuary and Gulf of St. Lawrence'
server = app.server

# Serve layout separately in order for page to always load this layout on default
def serve_layout():
    return html.Div(
        children=[
        html.Div(children=[html.H2("Estuary and Gulf of St. Lawrence: Temperatures, Salinity, and Fish Populations"),
                           html.P('This dashboard presents the evolution of Pelagic fish populations in the Gulf and Estuary of Saint Lawrence, Canada.'
                                  ' Evolution of temperature and salinity is presented as the average temperature per year, considering the month of April to September only'
                                  ' as the fish migrate to warmer waters in the winter. Other indicators that can have an impact on population, '
                                  'such as fishing and sailing activity, are not represented on this dashboard. Hence, the correlations presented on this map cannot be considered'
                                  ' a direct cause for fish population evolution.'),
                           ],
                 id='title', title='atitle', style={'marginBottom': 25}),
        html.Div(children=[
            html.Div(children=[html.H4('Fish Population'),
                               dcc.Dropdown(id='fish_dropdown', options=FISH_DROPDOWN, value='total'),
                               html.H4('Indicator'),
                               dcc.Dropdown(id='param_dropdown', options=PARAM_DROPDOWN, value='temperature'),
                               html.H4('Depth (meters)'),
                               dcc.Dropdown(id='depth_dropdown', options=DEPTH_DROPDOWN, value='0-100'),
                               dcc.Graph(id='indicator'),
                               ],
                     className='two columns'),
            html.Div(dcc.Graph(id='fish',config={'autosizable': True, 'displaylogo': False,
                                                 'displayModeBar': False}, style={'width': '100%'}),
                     className='ten columns')]),
        html.Div(children=[
            html.Div(html.H2('.'), className='two columns'),
            html.Div(children=[html.Header('Select a year to display change on the map'),
                               dcc.Slider(id='year-slider', min=2009, max=2018,
                                          value=2018, marks={year: str(year) for year in range(2009, 2019)},
                                          step=None)],
                     style={'marginBottom': 0}, className='ten columns')]),
        html.Div(children=[
            html.Div(dcc.Graph(id='temperature_graph', config={'autosizable': True, 'displayModeBar': False},
                               style={'width':'120%'}),
                     className='four columns'),
            html.Div(dcc.Graph(id='salinity_graph',  config={'autosizable': True, 'displayModeBar': False},
                               style={'width': '120%'}),
                     className='four columns'),
            html.Div(dcc.Graph(id='fish_graph',  config={'autosizable': True, 'displayModeBar': False},
                               style={'width':'120%'}),
                     className='four columns')
        ], className='twelve columns')])

app.layout = serve_layout

def get_color(color_value, param_value):
    if param_value not in ['temperature', 'salinity']:
        b_value = (color_value+5)/8*255
    elif param_value == 'temperature':
        b_value = (color_value-3)/8*255
    elif param_value == 'salinity':
        b_value = (color_value-30)/6*255
    else:
        b_value = 0

    # b_value should always be in the RGB range 0-255
    b_value = max(b_value, 0)
    b_value = min(b_value, 255)

    return f'rgb({b_value}, {b_value}, 255)'

# CALLBACK FOR THE FISH MAP
@app.callback(
    dash.dependencies.Output('fish', 'figure')
    , [dash.dependencies.Input('fish_dropdown', 'value'),
       dash.dependencies.Input('param_dropdown', 'value'),
       dash.dependencies.Input('depth_dropdown', 'value'),
       dash.dependencies.Input('year-slider', 'value')
       ])
def update_figure(fish_value, param_value, depth_value, year_value):
    # print(fish_value, param_value, depth_value, year_value)
    if fish_value=='total':
        locations = fish_locations[fish_locations['year']==year_value].copy()
    else:
        locations = fish_locations[(fish_locations['fish_type'] == fish_value) & (fish_locations['year']==year_value)].copy()

    color_value = param_data[(param_data.depth_range == depth_value)&(param_data.year == year_value)][param_value].item()
    # print(color_value)

    map_color = get_color(color_value, param_value)

    return {
        'data': [
            go.Densitymapbox(
                lat=locations['latitude'].tolist(),
                lon=locations['longitude'].tolist(),
                radius=10,
                showscale=False
            )
        ],

        'layout': go.Layout(autosize=True, hovermode='closest', height=600
                            , margin=dict(l=0, r=0, b=0, t=0, pad=0)
                            , mapbox = {'accesstoken': cfg.MAPBOX_TOKEN, 'bearing': 0, 'layers':
                [dict(sourcetype='geojson', source=gulf_geojson, type='fill', color=map_color)]
                    , 'center': {'lat': 48.3, 'lon': -64.5}, 'zoom': 5
                    , 'style': 'mapbox://styles/mapbox/light-v9'
                    }
        )
    }

def suffix_indicator(param_name):
    if param_name == 'temperature':
        return "° C"
    elif param_name == "salinity":
        return " PSU"
    else:
        return "No such parameter"

def correlation_score(fish_value, param_name, depth_value):
    # slightly faster calculations to correlations now since merge is done early on and this is just a filter.
    temp_df = correlation_table[(correlation_table['fish_type']==fish_value) & (correlation_table['depth_range']==depth_value)]
    corr = temp_df[param_name].corr(temp_df['fish_total'])
    # old correlation calculation - commented out for now for bug testing
    # fish = fish_data[['date', fish_value]].groupby('date').sum().reset_index().rename(columns={'date': 'year'})
    # param = param_data[param_data.depth_range == depth_value][['year', param_name]]
    # df = param.merge(fish, on='year')
    # old_corr = df[param_name].corr(df[fish_value])
    # print(corr, old_corr)
    # return old_corr
    return corr

# CALLBACK FOR THE STAT BAR
@app.callback(
    dash.dependencies.Output('indicator', 'figure')
    , [dash.dependencies.Input('fish_dropdown', 'value'),
       dash.dependencies.Input('param_dropdown', 'value'),
       dash.dependencies.Input('depth_dropdown', 'value'),
       dash.dependencies.Input('year-slider', 'value')
       ])
def update_indicators(fish_value, param_name, depth_value, year_value):
    df = param_data[param_data.depth_range == depth_value][['year', param_name]]
    avg_param = df.loc[(df['year'] == year_value), param_name].item()
    baseline_2009 = df.loc[(df['year'] == 2009), param_name].item()
    prev_year = df[param_name].shift(1).loc[df['year'] == year_value].item()
    unit = suffix_indicator(param_name)
    correlation = correlation_score(fish_value, param_name, depth_value)
    # print('correlation: ', correlation)

    return {
        'data': [
            go.Indicator(number={'suffix': unit, 'font.size':30}, value=avg_param,
                         title={
                             "text": f"<span style='font-size:2.5em'>Average {param_name}</span>"},
                         domain={'row': 0, 'column': 0}
                         ),
            go.Indicator(mode="delta", value=avg_param,
                         title={
                             "text": "<br><span style='font-size:3em;color:gray'>Since 2009</span><br><span style='font-size:0.8em;color:gray'></span>"},
                         # Plotly does not have suffix settings for delta yet. https://github.com/plotly/plotly.js/issues/4824
                         delta={'reference': baseline_2009, "valueformat": ".2f", 'font.size':20}, domain={'row': 1, 'column': 0}
                         ),
            go.Indicator(mode="delta", value=avg_param,
                         title={
                             "text": "<br><span style='font-size:3em;color:gray'>Since previous year</span><br><span style='font-size:0.8em;color:gray'></span>"},
                         delta={'reference': prev_year, "valueformat": ".2f", 'font.size':20},
                         domain={'row': 2, 'column': 0}
                         ),
            go.Indicator(number={"valueformat": ".2f", 'font.size':30}, value=correlation,
                         title={
                             "text": f"<span style='font-size:2.8em'>Correlation score <br></span>"
                                     f"<br><span style='font-size:1.5em;color:gray'>with {fish_value.replace('_', ' ')} population</span>"},
                         domain={'row': 4, 'column': 0}
                         )
        ],

        'layout': go.Layout(grid={'rows': 5, 'columns': 1, 'pattern': "independent"})
    }

# CALLBACK FOR THE TEMPERATURE CHART
@app.callback(
    dash.dependencies.Output('temperature_graph', 'figure')
    , [dash.dependencies.Input('depth_dropdown', 'value')
       ])
def update_temperature(depth_value):
    df = param_data[param_data.depth_range == depth_value][['year', 'temperature']]

    return {
        'data': [
            go.Scatter(x=df.year, y=df.temperature)
        ],
        'layout': go.Layout(title=f"Average April-September <br> Temperature Evolution - {depth_value}m")
    }

# CALLBACK FOR THE SALINITY CHART
@app.callback(
    dash.dependencies.Output('salinity_graph', 'figure')
    , [dash.dependencies.Input('depth_dropdown', 'value')
       ])
def update_salinity(depth_value):
    df = param_data[param_data.depth_range == depth_value][['year', 'salinity']]

    return {
        'data': [
            go.Scatter(x=df.year, y=df.salinity)
        ],
        'layout': go.Layout(title=f"Average April-September <br> Salinity Evolution - {depth_value}m")
    }

# CALLBACK FOR THE POPULATIOn CHART
@app.callback(
    dash.dependencies.Output('fish_graph', 'figure')
    , [dash.dependencies.Input('fish_dropdown', 'value')
       ])
def update_fish_graph(fish_value):
    fish_sum = fish_aggregate[fish_aggregate['fish_type']==fish_value].copy()
    fish_sum.sort_values(by='year', inplace=True)

    pop_2009 = fish_sum[fish_sum['year']==2009]['fish_total'].values[0]
    pop_2018 = fish_sum[fish_sum['year']==2018]['fish_total'].values[0]

    return {
        'data': [
            go.Indicator(mode="delta", value=pop_2018,
                         delta={'reference': pop_2009, 'relative': True, 'font.size': 28},
                         ),
            go.Scatter(x=fish_sum.year, y=fish_sum['fish_total'])
        ],

        'layout': go.Layout(title=f"{fish_value.replace('_', ' ').title()} <br> Population Evolution")
    }


if __name__== '__main__':
    app.run_server(debug=True)