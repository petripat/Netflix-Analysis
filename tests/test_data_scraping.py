import sys
import pathlib
sys.path.append(str(pathlib.Path().absolute()).split("/tests")[0])
import pandas as pd
from src.data_analysis import data_analysis, data_analysis_subtasks
from src.scraper.scrape_data import ScrapeData

path = str(pathlib.Path().absolute()).split("/tests")[0] + "/"

viewing_data_input = pd.DataFrame({'Title': pd.Series(['Father Hood', 'The Shawshank Redemption', 'The Big Bang Theory',
                                                       'Superstore', 'Little Women', "The Huntsman: Winter's War",
                                                       'Brooklyn Nine-Nine', 'Ženy v běhu', 'fasdfa'],
                                                      index=range(0, 9)),
                                   'Series': pd.Series(
                                       [False, False, True, True, False, False, True, False, False],
                                       index=range(0, 9))})

scrape_data_result = pd.DataFrame({'Title': pd.Series(['Father Hood', 'The Shawshank Redemption', 'The Big Bang Theory',
                                                       'Superstore', 'Little Women', "The Huntsman: Winter's War",
                                                       'Brooklyn Nine-Nine', 'Ženy v běhu', 'fasdfa'],
                                                      index=range(0, 9)),
                                   'Year Start': pd.Series(
                                       [1993, 1994, 2007, 2015, 2019, 2016, 2013, 2019, -1],
                                       index=range(0, 9)),
                                   'Year End': pd.Series(
                                       [1993, 1994, 2019, 2021, 2019, 2016, 2021, 2019, -1],
                                       index=range(0, 9)),
                                   'Genre': pd.Series(
                                       ['Komedie', 'Drama,Krimi', 'Komedie,Romantický', 'Komedie',
                                        'Drama,Romantický', 'Akční,Dobrodružný,Drama,Fantasy',
                                        'Komedie,Krimi', 'Komedie', '-'],
                                       index=range(0, 9)),
                                   'Country': pd.Series(
                                       ['USA', 'USA', 'USA', 'USA', 'USA', 'USA', 'USA', 'Česko', '-'],
                                       index=range(0, 9)),
                                   'Actors': pd.Series(
                                       ['Patrick Swayze,Halle Berry,Sabrina Lloyd,Brian Bonsall,Michael Ironside',
                                        'Tim Robbins,Morgan Freeman,Bob Gunton,William Sadler,Clancy Brown',
                                        'Johnny Galecki,Jim Parsons,Kaley Cuoco,Simon Helberg,Kunal Nayyar',
                                        'America Ferrera,Ben Feldman,Lauren Ash,Mark McKinney,Nichole Sakura',
                                        'Saoirse Ronan,Emma Watson,Florence Pugh,Eliza Scanlen,Laura Dern',
                                        'Chris Hemsworth,Jessica Chastain,Emily Blunt,Charlize Theron,Nick Frost',
                                        'Andy Samberg,Stephanie Beatriz,Terry Crews,Joe Lo Truglio,Melissa Fumero',
                                        'Zlata Adamovská,Tereza Kostková,Veronika Khek Kubařová,Jenovéfa Boková,Ondřej Vetchý',
                                        '-'],
                                       index=range(0, 9), dtype='str'),
                                   'Rating': pd.Series(
                                       [49, 95, 89, 75, 77, 59, 84, 70, -1],
                                       index=range(0, 9))
                                   })


def test_data_scraping():
    """Test for scraper class ScrapeData. """
    scraper = ScrapeData(viewing_data_input)
    scraper.start_scraping()
    pd.util.testing.assert_frame_equal(scraper.scraped_table, scrape_data_result)
    assert (scraper.scraped_table.equals(scrape_data_result))


dataForScraping = pd.read_csv(path + 'tests/data_for_test/data_add_scraped_data.csv')


def test_add_scraped_data():
    """Test for starting scraping and connecting scraped data (scraping tested in function above) with regular
    - fuction in data_analysis  add_scraped_data
    """
    data = data_analysis.prepare_data(dataForScraping)
    data = data_analysis.add_scraped_data(data, 'Daniel')
    result = pd.read_csv(path + 'tests/data_for_test/result_add_scraped_data.csv')
    result.Duration = result.Duration.apply(data_analysis_subtasks.make_delta)
    pd.util.testing.assert_frame_equal(data, result)
    assert (data.equals(result))


