import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import json
from helper import db
import pandas as pd
from helper import config as cfg
from pandas.api.types import CategoricalDtype


def make_categorical(df):
    '''Generates intervals of type '0-100' then map them to the depth column to make it categorical.'''
    intervals = ["{}-{}".format(i * 100, (i + 1) * 100) for i in range(60)]

    cat_type = CategoricalDtype(categories=intervals, ordered=True)
    df["depth_range"] = df["depth_range"].astype(cat_type)
    return df


def param_data():
    '''Return a dataframe with average temperature and salinity by depth and year,
    temperature and salinity evolution compared to 2009 and year over year temperature and salinity evolution.
    The SQL query filters outlier data (e.g. temperature below -2.5 or above 40 degrees celsius) and only takes values
    for the months of April to September (2009-2018) since these are the months the fish live in the Estuary.'''

    # The regex will remove brackets and parentheses from the depth column and avoid (0, 100], [0, 100) issues.
    # Include 'AND in_gulf = 1' to the filter when the gstpp data is all added.
    query = """
    SELECT
    extract(year from data_date) as year,
    REGEXP_REPLACE(depth, '[\[\]\(\)]', '', 'g') as depth_range,
    ROUND(AVG(temperature), 3) as temperature,
    ROUND(AVG(salinity), 3) as salinity
    FROM OCEAN_DATA
    WHERE data_date BETWEEN '2009-01-01' AND '2018-12-31'
    AND salinity BETWEEN 30 and 41
    AND temperature BETWEEN -2.5 and 40
    AND to_char(data_date,'Mon') in ('Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep')
    AND depth <> 'nan'
    AND in_gulf = 1
    GROUP BY year, depth_range
    ORDER BY year, temperature;
    """
    param_df = db.run_query(query)

    # Turn the depth_range column values back into categories. Start by replacing commas by hyphen and removing the white space.
    param_df['depth_range'] = param_df['depth_range'].str.replace(r"\, ", "-")
    param_df = make_categorical(param_df)

    # Change temp and salinity to floats
    param_df["temperature"] = param_df["temperature"].astype(float)
    param_df["salinity"] = param_df["salinity"].astype(float)

    # Make the year column a string
    param_df['year'] = param_df['year'].astype(int).astype(str)

    return param_df.reset_index(drop=True)


gulf_geojson = json.load(open('assets/iho.json'))
# fish_data = db.run_query()
fish_data = pd.read_csv('test.csv') # dummy query to avoid hitting up RDS for testing
fish_data.date = pd.to_datetime(fish_data.date).dt.year # will need to import date as year
fish_data['total'] = fish_data.iloc[:, 5:-1].sum(axis=1) # we need to calculate total population as well
#param_data = param_data()
param_data = pd.read_csv('sample_param_data.csv') # same as above, code in jupyter notebook - will add it to this file later.


def build_fish_dropdown():
    not_fish = ['date', 'station', 'longitude', 'latitude', 'depth', 'region']
    dropdown_labels = [{'label': i, 'value': i} for i in fish_data.columns if i not in not_fish]
    return dropdown_labels

def build_param_dropdown():
    dropdown_labels = [{'label': i, 'value': i} for i in ['temperature', 'salinity']]
    return dropdown_labels

def build_depth_dropdown():
    dropdown_labels = [{'label': i, 'value': i} for i in sorted([i for i in param_data.depth_range.unique()])]
    return dropdown_labels

def build_graph(id_name):
    return html.Div([dcc.Graph(id=id_name)], className='one-third column',
                    style={'marginBottom': 25, 'marginTop': 25}
                    ),

# Note that static assets such as html and the like must be served from the asset folders because Dash is pain
app = dash.Dash(__name__)
app.title = 'Ocean Temperature and Salinity in the Estuary and Gulf of St. Lawrence'
server = app.server


# Serve layout separately in order for page to always load this layout on default
def serve_layout():
    fish_name = build_fish_dropdown()
    param_name = build_param_dropdown()
    depth_interval = build_depth_dropdown()
    return html.Div(
        children=[
        html.Div(children=[html.H2("Estuary and Gulf of St. Lawrence: Temperatures, Salinity, and Fish Populations"),
                           html.P('This dashboard presents the evolution of Pelagic fish populations in the Gulf and Estuary of Saint Lawrence, Canada.'
                                  'Evolution of temperature and salinity is presented as the average temperature per year, considering the month of April to September only'
                                  'as the fish migrate to warmer waters in the winter. Other indicators that can have an impact on population, '
                                  'such as fishing and sailing activity, are not represented on this dashboard. Hence, the correlations presented on this map cannot be considered'
                                  'a direct cause for fish population evolution.'),
                           ],
                 id='title', title='atitle', style={'marginBottom': 25}),
        html.Div(children=[
            html.Div(children=[html.H4('Fish Population'),
                               dcc.Dropdown(id='fish_dropdown', options=fish_name, value='total'),
                               html.H4('Indicator'),
                               dcc.Dropdown(id='param_dropdown', options=param_name, value='temperature'),
                               html.H4('Depth'),
                               dcc.Dropdown(id='depth_dropdown', options=depth_interval, value='0-100'),
                               dcc.Graph(id='indicator'),
                               ],
                     className='two columns'),
            html.Div(dcc.Graph(id='fish',config={'autosizable': True, 'displaylogo': False,
                                                 'displayModeBar': False}, style={'width': '100%'}),
                     className='ten columns')]),
        html.Div(children=[
            html.Div(html.H2('-'), className='two columns'),
            html.Div(children=[html.Header('Select a year to display change on the map'),
                               dcc.Slider(id='year-slider', min=2009, max=2018,
                                          value=2018, marks={year: str(year) for year in range(2009, 2019)},
                                          step=None)],
                     style={'marginBottom': 25}, className='ten columns')]),
        html.Div(children=[
            html.Div(dcc.Graph(id='temperature_graph'), className='one-third column'),
            html.Div(dcc.Graph(id='salinity_graph'), className='one-third column'),
            html.Div(dcc.Graph(id='fish_graph'), className='one-third column')
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

    map_color = get_color(color_value, param_value)

    return {
        'data': [
            go.Densitymapbox(
                lat=fish_data[(fish_data[fish_value] > 0) & (fish_data.date == year_value)]['latitude'].tolist(),
                lon=fish_data[(fish_data[fish_value] > 0) & (fish_data.date == year_value)]['longitude'].tolist(),
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
        return "°C"
    elif param_name == "salinity":
        return "PSU"
    else:
        return "No such parameter"

def correlation_score(fish_value, param_name, depth_value):
    fish = fish_data[['date', fish_value]].groupby('date').sum().reset_index().rename(columns={'date': 'year'})
    param = param_data[param_data.depth_range == depth_value][['year', param_name]]
    df = param.merge(fish, on='year')
    #return df[fish_value].corr(df[param_name])
    return df[param_name].corr(df[fish_value])

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
    print('correlation: ', correlation)

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
                                     f"<br><span style='font-size:2em;color:gray'>with {fish_value} population</span>"},
                         domain={'row': 4, 'column': 0}
                         )
        ],

        'layout': go.Layout(grid={'rows': 5, 'columns': 1, 'pattern': "independent"})
    }

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

        'layout': go.Layout(title=f"Average April-September Temperature Evolution - {depth_value}m")
    }


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

        'layout': go.Layout(title=f"Average April-September Salinity Evolution - {depth_value}m")
    }

@app.callback(
    dash.dependencies.Output('fish_graph', 'figure')
    , [dash.dependencies.Input('fish_dropdown', 'value')
       ])
def update_fish_graph(fish_value):
    df = fish_data[['date', fish_value]].groupby('date').sum().reset_index()
    pop_2009 = df[fish_value].iloc[0]
    pop_2018 = df[fish_value].iloc[-1]

    return {
        'data': [
            go.Indicator(mode="delta", value=pop_2018,
                         delta={'reference': pop_2009, 'relative': True, 'font.size': 28},
                         ),
            go.Scatter(x=df.date, y=df[fish_value])
        ],

        'layout': go.Layout(title=f"{fish_value} Population Evolution")
    }


if __name__== '__main__':
    app.run_server(debug=True)