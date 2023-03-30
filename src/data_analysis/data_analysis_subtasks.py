import math
from datetime import datetime
from datetime import timedelta
import pandas as pd
import re
import streamlit as st
import plotly.graph_objects as go


def start_time_to_date_only(date):
    """
    Returns dataframe that modifies string date '%Y-%m-%d %H:%M:%S' for %Y-%m-%d datetime
    """
    tmp = date.copy()
    tmp['Start Time'] = tmp['Start Time'].apply(select_date)
    return tmp


def start_time_to_time_only(data: pd.DataFrame):
    """
    Returns dataframe that modifies string date '%Y-%m-%d %H:%M:%S' for '%H:%M:%S' time part datetime
    """
    tmp = data.copy()
    tmp['Start Time'] = tmp['Start Time'].apply(select_time)
    return tmp


def make_delta(entry: str):
    """
    From given string that should be in format of %H:%M:%S return pd.Timedelta
    """
    h, m, s = entry.split(':')
    return pd.Timedelta(hours=int(h), minutes=int(m), seconds=int(s))


def select_date(entry: str):
    """
    From given string that should be in format of %Y-%m-%d %H:%M:%S returns date part datetime %Y-%m-%d
    """
    return datetime.strptime(entry, '%Y-%m-%d %H:%M:%S').date()


def select_dayofweek(entry: str):
    """
    From given string that should be in format of %Y-%m-%d %H:%M:%S return weekday datetime
    """
    return datetime.strptime(entry, '%Y-%m-%d %H:%M:%S').weekday()


def select_month(entry: str):
    """
    From given string that should be in format of %Y-%m-%d %H:%M:%S returns month
    """
    return datetime.strptime(entry, '%Y-%m-%d %H:%M:%S').month


def select_time(entry: str):
    """
    Returns datetime, from '%Y-%m-%d %H:%M:%S' string date, with '%H:%M:%S' time part
    """
    return datetime.strptime(entry, '%Y-%m-%d %H:%M:%S').time()


def transform_to_hours(entry):
    """
    Transforms given pd.Timedelta to hours and returns float with hours
    """
    days, hours, min, sec, mlsec, microsec, nanosec = entry.components
    return days * 24 + hours + (min / 60) + (sec / (60 * 60))


def transform_to_minutes(entry):
    """
    Transforms given pd.Timedelta to minutes and returns float with minutes
    """
    days, hours, min, sec, mlsec, microsec, nanosec = entry.components
    return days * 24 * 60 + hours * 60 + min + sec / 60


def get_string_values_from_dataframe(data: pd.DataFrame, column: str):
    """
    From given dataframe and column extracts all strings in format str,str2 and puts them dividid in one dataframe that
    is returned
    """
    array = []
    df = pd.DataFrame({})
    df[column] = data[column].dropna()
    for val in df[column]:
        tmp = val.split(',')
        array.extend(tmp)
    df_values = pd.DataFrame({column: array})
    return df_values


def is_genre_in_str(genre: str, all_genres: str):
    """
    Checks if given string genre is in string all genres
    returns true yes, false no
    """
    if re.search(('.*' + genre + '.*'), all_genres) is not None:
        return True
    return False


def show_titles_table(dfs: pd.Series):
    """
    Sorts given dataframe by duration and shows it on web page.
    returns None
    """
    dfs = dfs.sort_values(by='Duration', ascending=False)
    dfs = dfs.rename({'Start Time': 'Times watched'})
    st.dataframe(dfs)


def print_pretty(entry):
    """
    Prints pretty pd.Timedelta on web page.
    returns None
    """
    days, hours, min, sec, mlsec, microsec, nanosec = entry.components
    if days > 0:
        return '{:02} days {:02}h {:02}m {:02}s'.format(int(days), int(hours), int(min), int(sec))
    elif hours > 0:
        return '{:02}h {:02}m {:02}s'.format(int(hours), int(min), int(sec))
    else:
        return '{:02}m {:02}s'.format(int(min), int(sec))


def markdown(entry_black: str, entry_blue: str):
    """
    Code for printing on streamlit webpage one part black and other red-ish (salmon)
    returns None
    """
    st.markdown(
        '''<span style="color:black; font-size: 14px">''' +
        entry_black
        + '''</span>
        <span style="color:Salmon; font-size: 14px">*''' +
        entry_blue +
        '''*</span> ''',
        unsafe_allow_html=True
    )


def markdown_graph_title(entry_black):
    """
    Prints title of graph/table/some important part on streamlit page.
    Returns None
    """
    st.markdown(
        '''<span style="color:black; font-size: 20px">''' +
        entry_black
        + '''</span>''',
        unsafe_allow_html=True
    )


def position_in_family_watching(df: pd.DataFrame, name: str):
    """
    Returns position in family in bz most time spent.
    Returns duration.
    """
    profiles = df.groupby('Profile Name').Duration.sum()
    profiles = profiles.sort_values(ascending=False)
    pos = 0
    for i, x in profiles.items():
        pos += 1
        if i == name:
            return pos


def make_timedelta_from_hours(hours):
    """
    From given float of hours returns made pd.Timedelta
    """
    days = hours / 24
    hours -= days * 24
    hours = math.floor(hours)
    hours -= hours
    minute = hours * 60
    seconds = (hours - minute / 60) * 60 * 60
    return pd.Timedelta(days=days, hours=int(hours), minutes=int(minute), seconds=int(seconds))


def most_common_watched_titles(data: pd.DataFrame, episodes: bool, sum: bool):
    """
    Returns dataframe with most common watched titles, if sum is true then it is returned based on sum of time spent
     watching else on count of time spent watching. If episodes are true then name of episodes is split to have only
     name part not episode part.
    """
    tmp = data.copy()
    tmp['Start Time'] = tmp['Start Time'].apply(select_date)
    tmp = tmp.drop_duplicates(['Start Time', 'Title'])
    if episodes:
        tmp['Title'] = tmp['Title'].apply(split_title)
    if sum:
        return tmp.groupby(['Title'])['Duration'].sum().sort_values(ascending=False)
    else:
        return tmp.groupby(['Title'])['Start Time'].count().sort_values(ascending=False)


def join_most_common_watched_titles(data: pd.DataFrame, episodes=False):
    """
    Returns dataframe with most watched titles and sum of time spent watching and count of times watched.
    """
    data1 = most_common_watched_titles(data, episodes, True)
    data2 = most_common_watched_titles(data, episodes, False)
    df = pd.merge(data1, data2, on='Title')
    df['Duration'] = df['Duration'].apply(str)
    return df


def data_country_timeline(data: pd.DataFrame, country: str):
    """
    Returns dataframe with time spent watching in given country over years - columns: Years, Duration, Time In Hours
    """
    tmp = data[data.Country == country].groupby('Start Time').Duration.sum()
    grouped = pd.DataFrame({'Date': tmp.index.copy(),
                            'Duration': tmp.values.copy()})
    grouped['Time In Hours'] = round(grouped['Duration'].apply(transform_to_hours), 2)
    grouped['Date'] = grouped['Date'].apply(select_date)
    return grouped


def graph_history_country(data: pd.DataFrame):
    """
    Graphs graph telling how much user watched netflix in different countries over years - from each country
    is called function data_country_timeline.
    Returns None
    """
    countries = data.Country.unique()
    layout = go.Layout(
        xaxis=dict(
            title="Date"
        ),
        yaxis=dict(
            title="Time spent watching in hours"
        ))
    fig = go.Figure(layout=layout)
    for country in countries:
        grouped = data_country_timeline(data, country)
        fig.add_bar(name=country, x=grouped.Date, y=grouped['Time In Hours'], hovertext=grouped.Duration.apply(str))
    fig.update_traces(dict(marker_line_width=0))
    fig.update_layout(showlegend=True)
    st.plotly_chart(fig)


def get_rating_df(data: pd.DataFrame):
    """
    Returns dataframe with all possible names of Title and it's Rating
    """
    df = data.drop_duplicates('Split Title')
    return pd.DataFrame({'Title': df['Split Title'],
                         'Rating': df['Rating']}).reset_index(drop=True)


def get_rating_over_years(df: pd.DataFrame):
    """
    Returns dataframe with columns Year and Average Rating, that tells user what was average rating over years of
    movies/series they watched.
    """
    data = df.copy()
    data['Start Time'] = data['Start Time'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S').year)
    year_start = data['Start Time'].min()
    year_end = data['Start Time'].max()
    years = pd.DataFrame({'Year': range(year_start, year_end + 1),
                          'Rating Sum': 0,
                          'Rating Count': 0})
    for rating, year in zip(data['Rating'], data['Start Time']):
        years.loc[years.Year == year, 'Rating Sum'] += rating
        years.loc[years.Year == year, 'Rating Count'] += 1
    years = pd.DataFrame({'Year': years['Year'],
                          'Average Rating': round(years['Rating Sum'] / years['Rating Count'], 2)}).sort_values('Year')
    return years


def get_rating_timeline(data: pd.DataFrame):
    """
    Returns dataframe with data about users watching and how was rated movies that user watched.
    """
    df = data.copy()
    df = start_time_to_date_only(df)
    timeline = df.groupby(df['Start Time']).Rating.mean()
    df = pd.DataFrame({'Date': timeline.index,
                       'Average Rating': timeline.values}).reset_index(drop=True)
    df['Average Rating'] = round(df['Average Rating'], 2)
    return df


# tests in get_time_table
def add_to_time_table(table: pd.DataFrame, row: pd.Series):
    """
    Add minutes data from Duration and starts time to dataframe with columns Hour, Time In Minutes that is returned.
    """
    hour = row[1].hour
    minutes = row[1].minute
    second = row[1].second
    minutes += second / 60
    total_min_watched = row[2]
    if total_min_watched - (60 - minutes) < 0:
        table.loc[(table['Hour'] == hour), 'Time In Minutes'] += total_min_watched
        return
    table.loc[(table['Hour'] == hour), 'Time In Minutes'] += (60 - minutes)
    hour += 1
    total_min_watched -= (60 - minutes)
    hour_in_min = math.floor(total_min_watched / 60)
    total_min_watched -= hour_in_min * 60
    if hour_in_min != 0:
        table.loc[(table.Hour.isin(range(hour, hour + hour_in_min))), 'Time In Minutes'] += 60
    table.loc[(table['Hour'] == hour + hour_in_min), 'Time In Minutes'] += total_min_watched


# tests in get_time_table
def join_time_table(table: pd.DataFrame):
    """
    Dataframe modifies and returns only 24 hours with sum of minutes.
    """
    nmp = table['Time In Minutes'].to_numpy()
    for i in range(0, 9):
        nmp[i] += nmp[i + 24]


def get_time_table(data: pd.DataFrame):
    """
    Returns pd.Dataframe with columns Hour, Time In Minutes for overview what hour user watch how much.
    """
    tmp = data.copy()
    tmp.Duration = tmp.Duration.apply(transform_to_minutes)
    tmp['Start Time'] = tmp['Start Time'].apply(select_time)
    table = pd.DataFrame({'Hour': range(0, 33),
                          'Time In Minutes': 0})
    tmp = tmp[['Start Time', 'Duration']]
    for row in tmp.itertuples():
        add_to_time_table(table, row)
    join_time_table(table)
    table = table.drop(range(24, 33))
    return table


def split_title(entry):
    """
    Returns from given string only main name part. For movies, no change is made but for series is removed episode and season
    part.
    """
    tmp = entry
    arr = entry.split(':')
    if re.search(".+Episode [0-9]+.*$", arr[-1]) is not None:
        return arr[0]
    return tmp
