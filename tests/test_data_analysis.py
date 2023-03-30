import sys
import pathlib
sys.path.append(str(pathlib.Path().absolute()).split("/tests")[0])
import pytest
import pandas as pd
from src.data_analysis import data_analysis, data_analysis_subtasks


path = str(pathlib.Path().absolute()).split("/tests")[0] + "/"

viewing_act = pd.read_csv(path + 'netflix-report/CONTENT_INTERACTION/ViewingActivity.csv')
viewing_act.Duration = viewing_act.Duration.apply(data_analysis_subtasks.make_delta)


# excpexted data from excel spreadsheat
@pytest.mark.parametrize(
    ['data', 'name', 'expected'],
    [(viewing_act, 'Daniel', 914.636944444444),
     (viewing_act, 'Kokos', 822.823611111111),
     (viewing_act, 'Patricie', 1514.66361111111),
     (viewing_act, 'Dagmar', 1660.72166666667)],
)
def test_hours_watched(data, name, expected):
    result = data_analysis.hours_watched(data[data['Profile Name'] == name])
    days, hours, min, sec, mlsec, microsec, nanosec = result.components
    hours = days * 24 + hours + (min / 60) + (sec / (60 * 60))
    assert (abs(expected - hours) < 0.1)


@pytest.mark.parametrize(
    ['data', 'name', 'expected'],
    [(viewing_act, 'Daniel', 2636),
     (viewing_act, 'Kokos', 2776),
     (viewing_act, 'Patricie', 5698),
     (viewing_act, 'Dagmar', 4643)],
)
def test_times_watched(data, name, expected):
    result = data_analysis.times_watched(data[data['Profile Name'] == name])
    assert (expected == result)


@pytest.mark.parametrize(
    ['data', 'name', 'expected'],
    [(viewing_act, 'Daniel', 0.346979113977407),
     (viewing_act, 'Kokos', 0.296406199967979),
     (viewing_act, 'Patricie', 0.26582372957373),
     (viewing_act, 'Dagmar', 0.357759945425822)],
)
def test_average_time(data, name, expected):
    data = data[data['Profile Name'] == name]
    result = data_analysis.avarage_time_spent_watching(data, data_analysis.times_watched(data))
    assert (abs(expected - result) < 0.1)


@pytest.mark.parametrize(
    ['data', 'name', 'expected'],
    [(viewing_act, 'Daniel', 2 * 60 + 39 + 43 / 60),
     (viewing_act, 'Kokos', 2 * 60 + 11 + 56 / 60),
     (viewing_act, 'Patricie', 2 * 60 + 4 + 53 / 60),
     (viewing_act, 'Dagmar', 2 * 60 + 55 + 29 / 60)],
)
def test_time_max(data, name, expected):
    result = data_analysis.max_time_watched_session(data[data['Profile Name'] == name])
    days, hours, min, sec, mlsec, microsec, nanosec = result.components
    result = days * 24 * 60 + hours * 60 + min + sec / 60
    assert (abs(expected - result) < 0.1)


dataForMax = pd.read_csv(path + 'tests/data_for_test/ViewingActivity0.csv')
dataForMax.Duration = dataForMax.Duration.apply(data_analysis_subtasks.make_delta)


@pytest.mark.parametrize(
    ['data', 'name', 'expected'],
    [(dataForMax, 'Daniel', 2 + 21 / 60 + 28 / 3600),
     (dataForMax, 'Patricie', (7 + 13 + 21 + 8 + 11) / 60 + (45 + 9 + 18 + 30 + 43) / 3600),
     (dataForMax, 'Dagmar', 1 + (13 + 33 + 0 + 27 + 59) / 60 + (16 + 38 + 0 + 31 + 7 + 6) / 3600)],
)
def test_max_time_watched_day(data, name, expected):
    data = data[data['Profile Name'] == name]
    result = data_analysis.max_time_watched_day(data)
    result = data_analysis_subtasks.transform_to_hours(result)
    assert (result - expected < 0.1)


dataForTimetable = pd.read_csv(path + 'tests/data_for_test/ViewingActivity1.csv')
dataForTimetable.Duration = dataForTimetable.Duration.apply(data_analysis_subtasks.make_delta)


def test_timetable():
    my_table = pd.DataFrame({'Hour': range(0, 24),
                             'Time In Minutes': pd.Series(
                                 [60 + 60, 60 + 30 / 60, 60, 1 + 1 / 60, 0, 8 + 29 / 60, 12 + 1 / 60, 0, 0, 0, 0, 0, 0,
                                  0, 0, 0, 0, 0, 10, 31 + 60 / 60, 6 + 30 / 60, 0, 30, 24 + 60 + 30 / 60],
                                 index=range(0, 24))})
    table = data_analysis_subtasks.get_time_table(dataForTimetable)
    my_table['Time In Minutes'] = my_table['Time In Minutes'].apply(lambda x: int(1000 * x))
    table['Time In Minutes'] = table['Time In Minutes'].apply(lambda x: int(1000 * x))
    assert (my_table.equals(table))


@pytest.mark.parametrize(
    ['entry', 'expected'],
    [("The Huntsman: Winter's War", "The Huntsman: Winter's War"),
     ("Blue Mountain State: Season 1: Promise Ring (Episode 2)", "Blue Mountain State"),
     ("Blue Mountain State: Season 1: Promise - - Ring (Episode 2)", "Blue Mountain State"),
     ("Blue Mountain State: Season 1: (Episode 2)", "Blue Mountain State"),
     ("Blue Mountain State: Season 1: Episode 2", "Blue Mountain State"),
     ("Blue Mountain State: Season 1: Promise 77 / 21 (Episode 2)", "Blue Mountain State"),
     ("Blue Mountain State: Promise Ring ", "Blue Mountain State: Promise Ring "),
     ("Blue Mountain State", "Blue Mountain State")]
)
def test_split_title(entry, expected):
    result = data_analysis_subtasks.split_title(entry)
    assert (result == expected)



def test_position_in_family_watching():
    assert(data_analysis_subtasks.position_in_family_watching(viewing_act, 'Daniel') == 3)
    assert(data_analysis_subtasks.position_in_family_watching(viewing_act, 'Patricie') == 2)
    assert(data_analysis_subtasks.position_in_family_watching(viewing_act, 'Kids') == 5)


def test_most_common_titles():
    dataForTitles = pd.read_csv(path + 'tests/data_for_test/ViewingActivity3.csv')
    dataForTitles.Duration = dataForTitles.Duration.apply(data_analysis_subtasks.make_delta)
    dataForTitles = dataForTitles[dataForTitles['Profile Name'] == 'Patricie']
    result = data_analysis_subtasks.most_common_watched_titles(dataForTitles, False, False)
    assert (result["Blue Mountain State: Season 1: Promise Ring (Episode 2)"] == 2)
    assert (result["Blue Mountain State: Season 1: Rivalry Weekend (Episode 4)"] == 2)
    assert (result["Blue Mountain State: Season 1: The Drug Olympics (Episode 6)"] == 2)
    assert (result["The Huntsman: Winter's War"] == 1)
    assert (result["The Huntsman: Winter's War"] == 1)
    result = data_analysis_subtasks.most_common_watched_titles(dataForTitles, True, False)
    assert (result["Blue Mountain State"] == 6)
    assert (result["The Huntsman: Winter's War"] == 1)
    assert (result["How I Met Your Mother"] == 3)


def test_get_actors():
    data = pd.read_csv(path + 'tests/data_for_test/result_add_scraped_data.csv')
    data_actors = pd.read_csv(path + 'tests/data_for_test/actors_only.csv')
    result = data_analysis_subtasks.get_string_values_from_dataframe(data, 'Actors')
    pd.util.testing.assert_frame_equal(data_actors, result)
    assert (data_actors.equals(result))


def test_dates_by_year_movie_came_out():
    data = pd.read_csv(path + 'tests/data_for_test/result_add_scraped_data.csv')
    cor_result = pd.DataFrame({'Year': pd.Series(
        [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
         2020, 2021, 2022],
        index=range(0, 16)),
        'Count of watched series/films': pd.Series(
            [1, 1, 1, 1, 1, 1, 2, 2, 3, 4, 3, 3, 5, 2, 3, 0],
            index=range(0, 16))})
    result = data_analysis.dates_by_year_movie_came_out(data)
    pd.util.testing.assert_frame_equal(cor_result, result)
    assert (cor_result.equals(result))


cor_result_drama = pd.DataFrame({'Year': pd.Series(
    [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
     2020, 2021, 2022],
    index=range(0, 16)),
    'Genre watched': pd.Series(
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0],
        index=range(0, 16))})

cor_result_comedy = pd.DataFrame({'Year': pd.Series(
    [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
     2020, 2021, 2022],
    index=range(0, 16)),
    'Genre watched': pd.Series(
        [2, 2, 2, 2, 2, 2, 4, 4, 5, 5, 5, 5, 6, 3, 3, 0],
        index=range(0, 16))})

scraped_data = pd.read_csv(path + 'tests/data_for_test/result_add_scraped_data.csv')
scraped_data['Duration'] = pd.to_timedelta(scraped_data['Duration'])


@pytest.mark.parametrize(
    ['cor_data', 'genre'],
    [(cor_result_drama, 'Drama'),
     (cor_result_comedy, 'Komedie')])
def test_years_of_genre(cor_data, genre):
    result = data_analysis.years_of_genre(scraped_data, genre)
    pd.util.testing.assert_frame_equal(result, cor_data)
    assert (cor_data.equals(result))


@pytest.mark.parametrize(
    ['genre', 'genres', 'expected'],
    [('Komedie', 'Komedie', True),
     ('Komedie', 'Komedie,', True),
     ('Komedie', ',Komedie,', True),
     ('Komedie', ',Drama,', False)])
def test_is_genre_in_str(genre, genres, expected):
    assert (data_analysis_subtasks.is_genre_in_str(genre, genres) == expected)


correct_result_country = pd.DataFrame({
    'Duration': pd.Series(['0 days 02:59:32', '0 days 00:12:42'], index=(1, 2)),
    'Times watched': pd.Series([8, 1], index=(1, 2))})
correct_result_country.set_index([['CZ (Czech Republic)', 'SK (Slovakia)']], inplace=True)
correct_result_origin = pd.DataFrame({
    'Duration': pd.Series(['0 days 02:54:49', '0 days 00:17:25'], index=(1, 2)),
    'Times watched': pd.Series([8, 1], index=(1, 2))})
correct_result_origin.set_index([['USA', 'Česko']], inplace=True)


@pytest.mark.parametrize(
    ['correct_result', 'column'],
    [(correct_result_country, 'Country'),
     (correct_result_origin, 'Country From')])
def test_country(correct_result, column):
    correct_result['Duration'] = pd.to_timedelta(correct_result['Duration'])
    result = data_analysis.analyze_country(scraped_data, column)
    pd.util.testing.assert_frame_equal(result, correct_result, check_names=False)
    assert (correct_result.equals(result))


# 'Percent': pd.Series(['0%',,,, 1], index=(0, 7)
def test_watching_habits():
    correct_result = pd.DataFrame({
        'Duration': pd.Series(['0 days 00:00:00', '0 days 01:04:24', '0 days 00:00:00', '0 days 00:50:11', '0 days '
                                                                                                           '00:52:15',
                               '0 days 00:00:00', '0 days 00:25:24'], index=range(0, 7)),
        'Time In Hours': pd.Series(range(0, 7), index=range(0, 7)),
        'Percent': pd.Series(['0.0%', '33.5%', '0.0%', '26.1%', '27.2%', '0.0%', '13.2%'], index=range(0, 7))
    })
    correct_result['Duration'] = pd.to_timedelta(correct_result['Duration'])
    correct_result['Time In Hours'] = round(correct_result.Duration.apply(data_analysis_subtasks.transform_to_hours), 2)
    correct_result.set_index([['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']],
                             inplace=True)
    result = data_analysis.watching_habit_days(scraped_data)
    pd.util.testing.assert_frame_equal(result, correct_result, check_names=False)
    assert(result.equals(correct_result))


def test_get_rating_df():
    correct_result = pd.DataFrame({'Title': pd.Series(['Fatherhood', 'Little Women', 'Ženy v běhu', "The Huntsman: "
                                                                                                    "Winter's War",
                                                       'Superstore', 'Brooklyn Nine-Nine', 'The Big Bang Theory'],
                                                      index=range(0, 7)),
                                   'Rating': pd.Series([61, 77, 70, 59, 75, 84, 89], index=range(0, 7)),
                                   })
    result = data_analysis_subtasks.get_rating_df(scraped_data)
    pd.util.testing.assert_frame_equal(result, correct_result, check_names=False)
    assert (result.equals(correct_result))


def test_get_rating_over_years():
    correct_result = pd.DataFrame({'Year': pd.Series([2020, 2021], index=range(0, 2)),
                                   'Average Rating': pd.Series([89, 72.86], index=range(0, 2)),
                                   })
    result = data_analysis_subtasks.get_rating_over_years(scraped_data)
    pd.util.testing.assert_frame_equal(result, correct_result, check_names=False)
    assert (result.equals(correct_result))

def test_rating_timeline():
    correct_result = pd.DataFrame({'Date': pd.Series(['2021-07-09', '2021-03-18', '2021-09-21', '2020-11-29'], index=range(0, 4)),
                                   'Average Rating': pd.Series([69.33, 59, 81, 89], index=range(0, 4))}).sort_values('Date').reset_index(drop=True)
    correct_result.Date = correct_result.Date.apply(str)
    result = data_analysis_subtasks.get_rating_timeline(scraped_data)
    result.Date = result.Date.apply(str)
    pd.util.testing.assert_frame_equal(result, correct_result, check_names=False)
    assert (result.equals(correct_result))


@pytest.mark.parametrize(
    ['input', 'correct_result'],
    [(2, pd.Timedelta(hours=2)),
     (24.15, pd.Timedelta(days=1, minutes=9)),
     (2.5, pd.Timedelta(hours=2, minutes=30)),
     (0, pd.Timedelta(hours=0))])
def test_make_time_delta_from_hours(input, correct_result):
    result = data_analysis_subtasks.make_timedelta_from_hours(input)
    assert(result == correct_result)


def test_data_country_timeline():
    correct_result = pd.read_csv(path + 'tests/data_for_test/country_time_correct.csv')
    correct_result['Duration'] = correct_result['Duration'].apply(data_analysis_subtasks.make_delta)
    result = data_analysis_subtasks.data_country_timeline(scraped_data, 'CZ (Czech Republic)')
    correct_result['Date'] = correct_result['Date'].apply(str)
    result['Date'] = result['Date'].apply(str)
    pd.util.testing.assert_frame_equal(result, correct_result, check_names=False)
    assert (result.equals(correct_result))