import pandas as pd
import numpy as np
import pathlib
from datetime import datetime
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import src.scraper.scrape_data
from src.data_analysis import data_analysis_subtasks



def analyse_users(data: pd.DataFrame):
    """Return dataframe with names of all users"""
    names = data['Profile Name'].unique()
    return names


def hours_watched(data: pd.DataFrame):
    '''
    Returns pd.Timedelta of all time spent watching netflix.
    '''
    return data.Duration.sum()


def times_watched(data: pd.DataFrame):
    '''Return how many times was series/movie turned on.'''
    return data.Duration.count()


def avarage_time_spent_watching(data: pd.DataFrame, v_times_watched):
    '''Return from data average time spent watching netflix.'''
    days, hours, min, sec, mlsec, microsec, nanosec = hours_watched(data).components
    return (days * 24 + hours + (min / 60) + (sec / (60 * 60))) / v_times_watched


def max_time_watched_session(data: pd.DataFrame):
    '''Return from data maximum time spent watching in one session.'''
    return data.Duration.max()


def max_time_watched_day(data: pd.DataFrame):
    '''Return from data maximum time spent watching in one day.'''
    tmp = data.copy()
    tmp['Start Time'] = tmp['Start Time'].apply(data_analysis_subtasks.select_date)
    tmp = tmp.groupby('Start Time').Duration.sum()
    return tmp.max()


def graph_time(data: pd.DataFrame):
    """
    Creates graph when user spents time watching during day - usual average. Data is sent to function that gets
    from given data table with 24 hours and how user watches and then this function graphs it.
    Return None
    """
    table = data_analysis_subtasks.get_time_table(data)
    table['Time In Hours'] = table['Time In Minutes'] / 60
    table['Percent'] = round(table['Time In Hours'] / table['Time In Hours'].sum() * 100, 1)
    table['Percent'] = table['Percent'].apply(str) + '%'
    fig = px.bar(table, x=table.Hour, y=table['Time In Hours'], text=table.Percent)
    fig.update_traces(marker_color="pink")
    st.plotly_chart(fig)


def analyse_country_data(data: pd.DataFrame, all: bool = True):
    """
    Function that calls functions to get date about watching in different countries and about origin of watched titles
    and writes it all out on web page.
    Return None
    """
    with st.expander("Country data"):
        tmp = data.copy()
        data_analysis_subtasks.markdown_graph_title('Countries streamed from with timeline')
        st.write("With double click you can show only one country. With one click you add/remove country.")
        data_analysis_subtasks.graph_history_country(tmp)
        tmp['Start Time'] = tmp['Start Time'].apply(data_analysis_subtasks.select_date)
        df = analyze_country(tmp, 'Country')
        df['Duration'] = df['Duration'].apply(str)
        data_analysis_subtasks.markdown_graph_title('Countries streamed from (table view)')
        st.dataframe(df)
        if all:
            df = analyze_country(tmp, 'Country From')
            data_analysis_subtasks.markdown_graph_title('Country of movies/series origin')
            df['Duration'] = df['Duration'].apply(str)
            st.dataframe(df)


def analyze_country(data: pd.DataFrame, column: str):
    """
    Return dataframe - table with time spent watching - duration and how many times user started watching based on given column in
    given dataframe.
    """
    countries_sum = data.groupby([data[column]]).Duration.sum()
    countries_count = data.groupby([column]).Duration.count()
    return pd.concat([countries_sum, countries_count], axis=1, keys=['Duration', 'Times watched'])


def watching_habits(data: pd.DataFrame):
    """
    Function that calls all other functions to get data about users watching habits and writes it out on page.
    Return None
    """
    with st.expander("Breakdown of watching time"):
        st.write("This graphs show your watching tendencies since subscription. For example, every year someone can "
                 "during the summer watch more than rest of the months or watches netflix always during evening. "
                 "If that is a case, it can be clearly seen in the graph.")
        data_analysis_subtasks.markdown_graph_title("Daytime watching overview")
        graph_time(data)
        data_analysis_subtasks.markdown_graph_title("Weekday overview of watching time")
        graph_watching_habit(watching_habit_days(data))
        data_analysis_subtasks.markdown_graph_title("Monthly overview of watching time")
        graph_watching_habit(watching_habit_months(data), 'indigo')
        data_analysis_subtasks.markdown_graph_title("Total timeline how you watched since subscription:")
        graph_watching_habit(watching_habit_timeline(data), 'midnightblue')


def watching_habit_months(df: pd.DataFrame):
    """
    Creates dataframe with columns Month, (pd.Timedelta), Time In Hours (Float in hours), Percent that tells when user
    spends time watching during months of the year - usual average.
    Returns dataframe
    """
    data = df.copy()
    name_cat = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
                'September', 'October', 'November', 'December']
    name_of_month = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
                     7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
    data['Start Time'] = data['Start Time'].apply(data_analysis_subtasks.select_month).map(name_of_month)
    data = data.rename(columns={'Start Time': "Month"})
    data = pd.DataFrame({'Duration': data.groupby('Month').Duration.sum().reindex(name_cat)})
    data['Duration'] = data['Duration'].fillna(pd.to_timedelta('00:00:00'))
    data['Time In Hours'] = data.Duration.apply(data_analysis_subtasks.transform_to_hours)
    data['Percent'] = round(data['Time In Hours'] / data['Time In Hours'].sum() * 100, 1)
    data['Percent'] = data['Percent'].apply(str) + "%"
    data['Time In Hours'] = round(data['Time In Hours'], 2)
    return data


def watching_habit_timeline(df: pd.DataFrame):
    """
    Creates dataframe with columns Date, Duration (pd.Timedelta), Time In Hours (Float in hours), Percent that tells
     how user watched Netflix since subscription.
     returns dataframe
    """
    data = df.copy()
    data['Start Time'] = data['Start Time'].apply(data_analysis_subtasks.select_date)
    data = data.rename(columns={'Start Time': "Date"})
    data = pd.DataFrame({'Duration': data.groupby('Date').Duration.sum()})
    data['Duration'] = data['Duration'].fillna(pd.to_timedelta('00:00:00'))
    data['Time In Hours'] = data.Duration.apply(data_analysis_subtasks.transform_to_hours)
    data['Percent'] = round(data['Time In Hours'] / data['Time In Hours'].sum() * 100, 1)
    data['Percent'] = data['Percent'].apply(str) + "%"
    data['Time In Hours'] = round(data['Time In Hours'], 2)
    return data


def watching_habit_days(df: pd.DataFrame):
    """
    Creates dataframe with columns Weekday (all days of week - from Monday), Duration (pd.Timedelta), Time In Hours
    (Float in hours), Percent that tells when user spends time watching during week - usual average.
    returns dataframe
    """
    data = df.copy()
    name_cat = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    name_of_day = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday',
                   6: 'Sunday'}
    data['Start Time'] = data['Start Time'].apply(data_analysis_subtasks.select_dayofweek).map(name_of_day)
    data = data.rename(columns={'Start Time': "Weekday"})
    data = pd.DataFrame({'Duration': data.groupby('Weekday').Duration.sum().reindex(name_cat)})
    data['Duration'] = data['Duration'].fillna(pd.to_timedelta('00:00:00'))
    data['Time In Hours'] = data.Duration.apply(data_analysis_subtasks.transform_to_hours)
    data['Percent'] = round(data['Time In Hours'] / data['Time In Hours'].sum() * 100, 1)
    data['Percent'] = data['Percent'].apply(str) + "%"
    data['Time In Hours'] = round(data['Time In Hours'], 2)
    return data


def graph_watching_habit(data: pd.DataFrame, color: str = 'mediumvioletred'):
    """
    Function that get data and graphs them using given color.
    X axis - index of data
    Y axis - Time In Hours column from data
    hover data - Duration - time spent watching but can be in pd.Timedelta
    Return None
    """
    data.Duration = data.Duration.apply(str)
    fig = px.bar(data, x=data.index, y='Time In Hours', hover_data=['Duration'], text=data.Percent)
    fig.update_traces(marker_color=color)
    fig.update_traces(dict(marker_line_width=0))
    st.plotly_chart(fig)


def analyze_watching_titles(data: pd.DataFrame, all: bool = True):
    """
    Function that calls function related to watching titles analysis - duration spent watching movies/series and writes
    it out on web page.
    Return None
    """
    with st.expander("Statistics of duration"):
        if all is False:
            st.info("If you watch less series than movies, then overall table is not relevant for you. In overall table"
                " you can also read name of episode while overview of series has only it's main name.")
        data_analysis_subtasks.markdown_graph_title("Most watched overall")
        data_analysis_subtasks.show_titles_table(data_analysis_subtasks.join_most_common_watched_titles(data))
        if all:
            data_analysis_subtasks.markdown_graph_title("Most watched movies")
            data_analysis_subtasks.show_titles_table(
                data_analysis_subtasks.join_most_common_watched_titles(data[data['Series'] == False]))
            data_analysis_subtasks.markdown_graph_title("Most watched series")
            data_analysis_subtasks.show_titles_table(
                data_analysis_subtasks.join_most_common_watched_titles(data[data['Series']], True))


def analyze_favorite_actor(data: pd.DataFrame):
    """
    Function that get table from function get_string_values_from_dataframe of actors and shows it on web page as plotly
     table.
     Return None
    """
    data_analysis_subtasks.markdown_graph_title("Actors watched the most")
    actors = data_analysis_subtasks.get_string_values_from_dataframe(data, 'Actors')
    actors = actors.groupby('Actors')['Actors'].count().sort_values(ascending=False)
    actors = actors.rename({'Actors': 'Actor'})
    fig = go.Figure(go.Table(header=dict(values=['Actor', 'Times watched']),
                             cells=dict(values=[actors.index, actors.values])))
    st.plotly_chart(fig)


def dates_by_year_movie_came_out(data: pd.DataFrame):
    """
    Function that returns dataframe with columns Year, Count of watched series/films that tells user years of
    movies/series that he prefers.
    Return dataframe
    """
    years_data = data.drop_duplicates('Split Title')
    year_start = data['Year Start'].min()
    year_end = datetime.now().year
    years = pd.DataFrame({'Year': range(year_start, year_end + 1),
                          'Count of watched series/films': 0})
    for year1, year2 in zip(years_data['Year Start'], years_data['Year End']):
        years.loc[years.Year.between(year1, year2), 'Count of watched series/films'] += 1
    return years


def analyze_years_series(data: pd.DataFrame):
    """
    Calls functions and show data on web page - which year user watches what.
    Return None
    """
    data_analysis_subtasks.markdown_graph_title("Graph with years of creation of movies/series you watch")
    st.write("If series is shot between more years, than to the graph is counted every year in the interval. "
             "So series made between years 2020-2021 is counted in graph to both yeats.")
    timeline = dates_by_year_movie_came_out(data)
    fig = px.bar(timeline, x='Year', y='Count of watched series/films', hover_data=['Count of watched series/films'])
    st.plotly_chart(fig)


@st.cache(suppress_st_warning=True, show_spinner=False)
def prepare_data(data):
    """
    Prepares data for analysis. Filters data and drops not used columns and makes pd.Timedelta from Start Time column.
    """
    data = data.drop(['Attributes', 'Supplemental Video Type', 'Device Type', 'Bookmark', 'Latest Bookmark'], axis=1)
    data.Duration = data.Duration.apply(data_analysis_subtasks.make_delta)
    delta = pd.Timedelta(hours=int(0), minutes=int(5), seconds=int(0))
    data = data[data.Duration > delta]
    return data


def analyze_rating(data: pd.DataFrame):
    """
    Function that calls other functions related to rating and show it on web page.
    Return None
    """
    with st.expander("Rating"):
        data_analysis_subtasks.markdown_graph_title("Rating of watched movies/series")
        st.write("Shows what is average rating by other people who watched it - from čsfd page.")
        rating_table = data_analysis_subtasks.get_rating_df(data)
        st.dataframe(rating_table)
        st.write('')
        data_analysis_subtasks.markdown_graph_title("Average yearly rating of all watched series/movies")
        col1, col2 = st.columns([1, 2])
        col1.write('')
        col1.write('')
        col1.write('')
        col1.write('')
        col1.write('')
        rating_table = data_analysis_subtasks.get_rating_over_years(data)
        rating_table.set_index('Year', inplace=True)
        col1.dataframe(rating_table)
        fig = px.bar(rating_table, x=rating_table.index, y='Average Rating', width=450, height=400)
        fig.update_traces(marker_color="indigo")
        fig.update_traces(dict(marker_line_width=0))
        fig.update_yaxes(range=[0, 100])
        col2.plotly_chart(fig)
        data_analysis_subtasks.markdown_graph_title("Rating of titles timeline")
        rating_table = data_analysis_subtasks.get_rating_timeline(data)
        # rating_table = rating_table.rename({'Average Rating': 'Rating'}) todo
        fig = px.bar(rating_table, x='Date', y='Average Rating')
        fig.update_yaxes(range=[0, 100])
        fig.update_traces(dict(marker_line_width=0))
        fig.update_traces(marker_color="salmon")
        st.plotly_chart(fig)


# tested
def years_of_genre(df: pd.DataFrame, genre: str):
    """
    Function that get table with columns Year, Genre watched that tells user based on which year movie was made which
    genre user prefers.
    Return dataframe
    """
    data = df.copy()
    year_start = data['Year Start'].min()
    year_end = datetime.now().year
    years = pd.DataFrame({'Year': range(year_start, year_end + 1),
                          'Genre watched': 0})
    for genres, year1, year2 in zip(data['Genre'], data['Year Start'], data['Year End']):
        if data_analysis_subtasks.is_genre_in_str(genre, genres):
            years.loc[years.Year.between(year1, year2), 'Genre watched'] += 1
    return years


# Division by countries
def years_of_genre_user(df: pd.DataFrame, genre: str):
    """
    Function that get table with columns Year, Genre watched that tells user what genres he watched over years.
    Return dataframe
    """
    data = df.copy()
    data['Start Time'] = data['Start Time'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S').year)
    year_start = data['Start Time'].min()
    year_end = data['Start Time'].max()
    years = pd.DataFrame({'Year': range(year_start, year_end + 1),
                          'Genre watched': 0})
    for genres, year in zip(data['Genre'], data['Start Time']):
        if data_analysis_subtasks.is_genre_in_str(genre, genres):
            years.loc[years.Year == year, 'Genre watched'] += 1
    return years


def years_of_genre_graph(data: pd.DataFrame, genres: list, start_time: bool = False):
    """
    Function that calls function to get data about user's genre preferences and graphs it.
    bool start_time - tells which function to get data to call for true years_of_genre_user(data, genre),
                false years_of_genre_(data, genre)
    Return None
    """
    layout = go.Layout(
        xaxis=dict(
            title="Date"
        ),
        yaxis=dict(
            title="Times watched"
        ))
    fig = go.Figure(layout=layout)
    max_genres = pd.DataFrame()
    first = True
    for genre in genres:
        if start_time:
            grouped = years_of_genre_user(data, genre)
        else:
            grouped = years_of_genre(data, genre)
        if first:
            max_genres['Year'] = grouped['Year']
        max_genres[genre] = grouped['Genre watched'].copy()
        years = grouped['Year']
        count = grouped['Genre watched']
        fig.add_bar(name=genre, x=years, y=count)
    fig.update_traces(dict(marker_line_width=0))
    st.plotly_chart(fig)
    max_genres = max_genres[max_genres.drop('Year', axis=1).sum(axis=1, numeric_only=True) != 0]
    max_genres['Genre'] = max_genres.loc[:, max_genres.columns != 'Year'].idxmax(axis=1)
    max_genres.rename({'Genre': 'Genre watched most'})
    fig_table = go.Figure(go.Table(header=dict(values=['Year', 'Genre watched most']),
                                   cells=dict(values=[max_genres['Year'], max_genres['Genre']])))
    st.plotly_chart(fig_table)


def analyze_genres_from_years(scraped_data: pd.DataFrame):
    """
    Layout of web page and calls functions related to watching genres which get data and graphs it.
    Return None
    """
    with st.expander("Genres"):
        st.write("First two graph shows your preferred genre by years that movie was made in. For example between "
                 "years 1990-2000"
                 " someone can mostly watch comedies while 2010-2020 drama because the drama was better. "
                 "So it shows how your preferences for movies change based on time they were filmed.")
        df_genres = data_analysis_subtasks.get_string_values_from_dataframe(scraped_data, 'Genre')
        genre_uniq = df_genres['Genre'].unique()
        data_analysis_subtasks.markdown_graph_title('Distribution of genres')
        years_of_genre_graph(scraped_data, genre_uniq)
        st.write("Another two graph shows you in what year you like which genre. For example one year somebody "
                 "preferred to watch comedy while another thriller. But it now doesn't evalueta the year movie was "
                 "made in. So it shows how your preferences for movies change over time.")
        data_analysis_subtasks.markdown_graph_title('Yearly genre overview')
        years_of_genre_graph(scraped_data, genre_uniq, True)


def first_watched(data):
    """
    Get's title, date and duration from data of user's first time watching Netflix and show's it on web page.
    Return None
    """
    first_watched_date = data['Start Time'].min()
    name_first_title = data.loc[data['Start Time'] == first_watched_date, 'Title'].head(1).item()
    duration_first_title = data.loc[data['Start Time'] == first_watched_date, 'Duration'].head(1).item()
    with st.expander("First time watched"):
        data_analysis_subtasks.markdown("\tYou watched:", name_first_title)
        data_analysis_subtasks.markdown("Date:", first_watched_date)
        data_analysis_subtasks.markdown("\tDuration:", data_analysis_subtasks.print_pretty(duration_first_title))


def analyse_overall_activity(df: pd.DataFrame, name: str, family: bool = True, title: str = ' '):
    """
    Layout of web page and calls functions related to overall activity of user on Netflix which get data and graphs it.
    Returns data filtered by given parameter name. Bool family and str title is for analysis of only one title, when \
    family should be False nad str title that is written with frunction information_one_title.
    Called functions: information_one_title, position_in_family_watching, times_watched, hours_watched,
                    max_time_watched_session, max_time_watched_day, avarage_time_spent_watching
    returns dataframe
    """
    data = df.copy()
    if family:
        position = data_analysis_subtasks.position_in_family_watching(df, name)
        data = data[data['Profile Name'] == name]
    v_times_watched = times_watched(data)
    with st.expander("Basic information"):
        if family:
            data_analysis_subtasks.markdown(
                "Position of watching time in family (based on overall duration):",
                str(position))
        data_analysis_subtasks.markdown("Overall duration of watching time (since subscription):",
                                        data_analysis_subtasks.print_pretty(hours_watched(data)))
        data_analysis_subtasks.markdown("Total number of times you started to watch title on Netflix: ",
                                        str(v_times_watched))
        data_analysis_subtasks.markdown("Average time in one session: ",
                                        str(data_analysis_subtasks.print_pretty(data_analysis_subtasks. \
                                            make_timedelta_from_hours(
                                            avarage_time_spent_watching(data, v_times_watched)))))
        data_analysis_subtasks.markdown("The longest watching session: ",
                                        data_analysis_subtasks.print_pretty(max_time_watched_session(data)))
        data_analysis_subtasks.markdown("Maximum watch time in one day: ",
                                        data_analysis_subtasks.print_pretty(max_time_watched_day(data)))
        if family is False:
            information_one_title(df, title)
    return data


def title_data(data: pd.DataFrame):
    """
    Makes page web payout of called functions for analysis of one title.
    Functions called: analyse_overall_activity, first_watched, watching_habits, analyze_watching_titles,
                      analyse_country_data
    returns None
    """
    a = st.radio("Would you like to know something about specific title?", ['Yes', 'No'], 1)
    if a == 'No':
        pass
    else:
        data_analysis_subtasks.markdown_graph_title("Basic information about specific title")
        names = data['Split Title'].drop_duplicates()
        option = st.selectbox('Which title are you interested in?', names)
        df = data[data['Split Title'] == option]
        analyse_overall_activity(df, ' ', False, option)
        first_watched(df)
        watching_habits(df)
        if df.drop_duplicates('Title').size > 1:
            analyze_watching_titles(df, False)
        analyse_country_data(df, False)


def information_one_title(df: pd.DataFrame, option: str):
    """
    Writes on web page information on Rating, Genre and Country of origin of given title.
    Returns None
    """
    data_analysis_subtasks.markdown('Rating of ' + option + '', str(df['Rating'].iloc[0]))
    genres = df['Genre'].iloc[0]
    genres = genres.split(',')
    genres = ', '.join(genres)
    data_analysis_subtasks.markdown('Genre of ' + option + '', genres)
    countries = df['Country From'].iloc[0]
    countries = countries.split('/')
    countries = ', '.join(genres)
    data_analysis_subtasks.markdown('Country of origin of ' + option + '', df['Country From'].iloc[0])


def analyse_viewing_activity(name: str, data: pd.DataFrame, scraped_data: pd.DataFrame):
    """
    Main function that calls all other function for all analysis for web page.
    returns None
    """
    first_watched(data[data['Profile Name'] == name])
    data = analyse_overall_activity(data, name)
    watching_habits(data)
    analyze_watching_titles(scraped_data)
    analyse_country_data(scraped_data)
    analyze_other(scraped_data)
    analyze_genres_from_years(scraped_data)
    analyze_rating(scraped_data)


@st.cache(suppress_st_warning=True, show_spinner=False)
def add_scraped_data(data: pd.DataFrame, name: str):
    """
    Function that from given dataframe prepares data for scraping and calls scraping class. After that merges scraped data
    with given and return dataframe with columns: Profile Name (str), Start Time (datetime), Duration (pd.Timedelta),
    Title (str), Country(str), Split Title (str), Series (bool), Year Start (int), Year End (int), Genre (str),
    Country From (str), Actors (str), Rating (int)
    """
    new_data = data[data['Profile Name'] == name].copy()
    data['Title'].count()
    new_data['Split Title'] = new_data['Title'].apply(data_analysis_subtasks.split_title)
    new_data['Series'] = np.where(new_data['Title'] == new_data['Split Title'], False,
                                  True)  # create a new column in df1 to check if prices match
    sdf = pd.DataFrame({'Title': new_data['Split Title'].copy(),
                        'Series': new_data['Series'].copy()})
    sdf = sdf.drop_duplicates()
    scrape = src.scraper.scrape_data.ScrapeData(sdf)
    sdf['Title'].count()
    with st.spinner(text="If you watch a lot, this could take a while. Fetching data for you."
                         + " This will take about: " + str(int((sdf['Title'].count() * 2.5)/60 + 1)) + " min"):
        scrape.start_scraping()
        scraped_data = scrape.get_scraped_data().copy()
        scraped_data = scraped_data[scraped_data['Year Start'] != -1]
        scraped_data = scraped_data.rename(columns={'Title': 'Split Title', 'Country': 'Country From'})
        new_data = pd.merge(new_data, scraped_data, on='Split Title')
    return new_data


def analyze_other(data: pd.DataFrame):
    """
    Shows on web page information about actors and from which years user watches series.
    Called functios: analyze_favorite_actor, analyze_years_series
    Returns None
    """
    with st.expander("Actors and years of origin"):
        analyze_favorite_actor(data)
        analyze_years_series(data)


def select_scraped_data(name):
    """
    Selects scraped data for dataframe for testing purposes.
    """
    path_m = str(pathlib.Path().absolute()).split("/src")[0]
    scraped_data = pd.read_csv(path_m + '/tests/scraped_data/' + name + '.csv')
    scraped_data.Duration = pd.to_timedelta(scraped_data.Duration)
    return scraped_data
