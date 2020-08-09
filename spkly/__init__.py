from IPython.display import HTML
import numpy as np
import io
import matplotlib.pyplot as plt


def display(df, order=None, type='line', max_rows=7, max_cols=999):
    ''' Builds a tiny sparkline for every numeric column of a given dataframe and integrates it as part of
    a dataframe column header. Sorry, does not accept Series as the moment!

    :param df: DataFrame object
    :param order: optional ordering scheme for the x-axis (otherwise defaults to the order in the dataframe)
    :param type of view you wanna see. at the most accepts 'line' (default), and 'histogram' (for histogram)
    :param max_rows: max rows displayed to the notebook
    :param max_columns: max columns displayed to the notebook
    :return: an HTML representation of the dataframe
    '''

    # python object handling doesn't make sense so imma make a copy for now until i get a handle on this
    temp_df = df.copy()
    # set up default ordering if none available
    if order is None:
        order = range(temp_df.shape[0])

    new_column_names_list = []
    # Determines which columns are numeric - changes based on a multilevel column
    if temp_df.columns.nlevels == 1:
        is_num = temp_df.select_dtypes(include=[np.number]).columns.values
    else:
        is_num = temp_df.select_dtypes(include=[np.number]).columns.levels[-1].values

    # iterates through each column and generates a matplotlib chart
    lowest_level = temp_df.columns.get_level_values(-1)
    for column_name, column_data in zip(lowest_level, range((len(temp_df.columns)))):
        if column_name in is_num:
            image = convert_fig(temp_df.iloc[:, column_data].values, order, type)
            new_column_name = column_name + image
            new_column_names_list.append(new_column_name)
        else:
            new_column_names_list.append(column_name)

    # replace column headers to include svg chart and renderrrrrrr away
    if temp_df.columns.nlevels == 1:
        temp_df.columns = new_column_names_list
    else:
        # build a column level mapper
        keys = list(lowest_level)
        values = new_column_names_list
        mapper = dict(zip(keys, values))
        temp_df.rename(columns=mapper, level=-1, inplace=True)
    return HTML(temp_df.to_html(escape=False, max_rows=max_rows, max_cols=max_cols))


def convert_fig(a_series, order, type):
    ''' Maps a numeric Series as a matplotlib chart and returns svg string

    :param a_series: Series to map
    :param order: specified xaxis for ordering
    :param type: type of chart generated
    :return svg representation of chart in utf-8
    '''

    # build tiny chart
    fig = plt.figure()
    fig.set_size_inches(3, .5)
    ax = fig.gca()
    if type == 'histogram':
        ax.hist(a_series[~np.isnan(a_series)], 20)  # 20 bins
    else:
        ax.plot(order, a_series)
    ax.axis('off')

    # save png to buffer
    buf = io.BytesIO()
    fig.savefig(buf, format='svg', bbox_inches='tight')
    buf.seek(0)
    encode = buf.getvalue().decode('UTF-8')
    plt.close(fig)  # this is to stop images from echoing to ipython
    return encode.replace('\r\n', '')
