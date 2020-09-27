import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import json
import pandas as pd
from helper import config as cfg
from pandas.api.types import CategoricalDtype
import generate_data as gd
import numpy as np
from sklearn.linear_model import LinearRegression

# DATA GENERATION
gulf_geojson = json.load(open('assets/iho.json'))
param_data = gd.get_param_data()
fish_aggregate = gd.get_fish_aggregate()
fish_locations = gd.get_fish_locations()
fish_info = gd.get_fish_info()
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
                               html.Div(children=['No fish data available.'], id='fish_infobox')
                               ],
                     className='three columns'),
            html.Div(dcc.Graph(id='fish',config={'autosizable': True, 'displaylogo': False,
                                                 'displayModeBar': False}, style={'width': '100%'}),
                     className='nine columns')]),
        html.Div(children=[
            html.Div(html.H4('.'), className='three columns'),
            html.Div(children=[html.Header('Select a year to display change on the map'),
                               dcc.Slider(id='year-slider', min=2009, max=2018,
                                          value=2018, marks={year: str(year) for year in range(2009, 2019)},
                                          step=None)],
                     style={'marginBottom': 15}, className='nine columns')]),
        html.Div(children=[
            html.Div(dcc.Graph(id='indicator', config={'displayModeBar': False}, style={'marginTop': 0}), className='three columns'),
            html.Div(dcc.Graph(id='temperature_graph', config={'autosizable': True, 'displayModeBar': False},
                               style={'width':'100%'}),
                     className='three columns'),
            html.Div(dcc.Graph(id='salinity_graph',  config={'autosizable': True, 'displayModeBar': False},
                               style={'width': '100%'}),
                     className='three columns'),
            html.Div(dcc.Graph(id='fish_graph',  config={'autosizable': True, 'displayModeBar': False},
                               style={'width':'100%'}),
                     className='three columns')
        ], className='twelve columns')])

app.layout = serve_layout

def get_color(color_value, param_value):
    '''Color formula:
     formula = (color_value - min_color_value) / color_value_range * scale_range + min_scale
    color_value_range = max_color_value - min_color_value
    scale_range = max_scale - min_scale
    '''
    if param_value not in ['temperature', 'salinity']:
        return 'rgb(255, 255, 255)', None
    elif param_value == 'temperature':
        r = (color_value - 2) / (12-2) * (191 - 96) + 96
        g = (color_value - 2) / (12-2) * (227 - 118) + 118
        b = (color_value - 2) / (12-2) * (225 - 198) + 198
        tick_vals = [0, 4, 8, 11]
    elif param_value == 'salinity':
        r = (color_value - 30) / (36-30) * (191 - 96) + 96
        g = (color_value - 30) / (36-30) * (227 - 118) + 118
        b = (color_value - 30) / (36-30) * (225 - 198) + 198
        tick_vals = [30, 32, 34, 36]

    # r should always be in the range 96-191
    r = (min(max(r, 96), 191))
    # g should always be in the range 118-227
    g = (min(max(g, 118), 227))
    # b should always be in the range 142-225
    b = (min(max(b, 142), 225))

    return f'rgb({r}, {g}, {b})', tick_vals

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

    map_color, map_colorscale = get_color(color_value, param_value)

    return {
        'data': [
            go.Densitymapbox(
                lat=locations['latitude'].tolist(),
                lon=locations['longitude'].tolist(),
                radius=10,
                showscale=False,
                hoverinfo='skip'
            ),
            # Creating hidden heatmap so that colorscale for parameter average can show on the right side of the plot
            go.Heatmap(
                z=[list(param_data[param_value]),
                   ],
                colorscale=[[0.0, "rgb(96,118,142)"],
                            [0.1, "rgb(106,129,150)"],
                            [0.2, "rgb(115,140,159)"],
                            [0.3, "rgb(125,151,167)"],
                            [0.4, "rgb(134,162,175)"],
                            [0.5, "rgb(144,173,184)"],
                            [0.6, "rgb(153,183,192)"],
                            [0.7, "rgb(163,194,200)"],
                            [0.8, "rgb(172,205,208)"],
                            [0.9, "rgb(182,216,217)"],
                            [1.0, "rgb(191,227,225)"]],
                colorbar=dict(
                    title=f"{param_value}",
                    titleside="top",
                    tickmode="array",
                    tickvals=map_colorscale,
                )
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
    temp_df = correlation_table[(correlation_table['fish_type']==fish_value) & (correlation_table['depth_range']==depth_value)]
    corr = temp_df[param_name].corr(temp_df['fish_total'])
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

def param_trend(depth_value, param_name):
    df = param_data[param_data.depth_range == depth_value][['year', param_name]]
    reg = LinearRegression().fit(np.vstack(df.year), df[param_name])
    df['bestfit'] = reg.predict(np.vstack(df.year))
    return df

# CALLBACK FOR THE TEMPERATURE CHART
@app.callback(
    dash.dependencies.Output('temperature_graph', 'figure')
    , [dash.dependencies.Input('depth_dropdown', 'value')
       ])
def update_temperature(depth_value):
    df = param_trend(depth_value, 'temperature')

    return {
        'data': [
            go.Scatter(name='', x=df.year, y=df.temperature, showlegend=False),
            go.Scatter(name='trend', x=df.year, y=df.bestfit, mode='lines', showlegend=False, opacity=0.5)
        ],
        'layout': go.Layout(title=f"Average April-September <br> Temperature Evolution - {depth_value}m",
                            margin=dict(l=40, r=0,b=100,t=50,pad=0))
    }

# CALLBACK FOR THE SALINITY CHART
@app.callback(
    dash.dependencies.Output('salinity_graph', 'figure')
    , [dash.dependencies.Input('depth_dropdown', 'value')
       ])
def update_salinity(depth_value):
    df = param_trend(depth_value, 'salinity')

    return {
        'data': [
            go.Scatter(name='', x=df.year, y=df.salinity, showlegend=False),
            go.Scatter(name='trend', x=df.year, y=df.bestfit, mode='lines', showlegend=False, opacity=0.5)
        ],
        'layout': go.Layout(title=f"Average April-September <br> Salinity Evolution - {depth_value}m",
                            margin=dict(l=40, r=0,b=100,t=50,pad=0))
    }

# CALLBACK FOR THE POPULATION CHART
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

        'layout': go.Layout(title=f"{fish_value.replace('_', ' ').title()} <br> Population Evolution",
                            margin=dict(l=40, r=0,b=100,t=50,pad=0),
                            )
    }

# CALLBACK FOR THE FISH INFO WINDOW
@app.callback(
    dash.dependencies.Output('fish_infobox', 'children')
    , [dash.dependencies.Input('fish_dropdown', 'value')
       ])
def update_fish_desc(fish_value):
    if fish_value not in fish_info['fish_value'].unique().tolist():
        return [html.P('Select fish population to access fish description.', style={'marginTop': 30})]
    else:
        info = fish_info[fish_info['fish_value']==fish_value]
        return [html.Img(src=info.picture.values[0], width='100%', style={'marginTop': 30, 'marginLeft':5}),
                html.Br(),
                dcc.Link(html.A(f'{info.picture_credits.values[0]}'), href=f'{info.credits_link.values[0]}', style={'fontSize': '12px'}),
                html.P(f'Depth Range: {info.depth_range.values[0]}', style={'fontSize': '14px'}),
                html.P(f'{info.fish_name.values[0].title()}: {info.description.values[0]}', style={'fontSize': '14px'}),
                dcc.Link(html.A('Fishbase Link'), href=f'{info.fishbase_link.values[0]}', style={'fontSize': '12px'})
                ]

if __name__== '__main__':
    app.run_server(debug=True)