import time
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup


class ScrapeData:
    """ Class that takes care of all data scraping.
         Attributes:
            session = session initialised by requests used for all data scraping
            self.table = pandas table with films to scrape
            self.headers = headers used for all data scraping
            self.base_url = 'https://www.csfd.cz'
            self.search_url = '/hledat/?q='
            self.response = attribute used to save response for made request used for scraping
            self.scraped_table = pandas table to save scraped data
        """

    def __init__(self, data):
        """
        Initialises all variable used for data scraping - session, headers, url
        :param data: DataFrame with name of Titles to scrape data for.
        """
        self.session = requests.Session()
        self.table = data.copy()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/96.0.4664.110 Safari/536.36'}
        self.base_url = 'https://www.csfd.cz'
        self.search_url = '/hledat/?q='
        self.response = None
        self.table = self.table.reset_index(drop=True)
        self.scraped_table = pd.DataFrame({'Title': data['Title'].copy(),
                                           'Year Start': -1,
                                           'Year End': -1,
                                           'Genre': '-',
                                           'Country': '-',
                                           'Actors': '-',
                                           'Rating': -1})

    def scrape_search_page(self, data_title: str, series: str):
        """
        Class that scrapes search page for correct title. Title is chosen based on if it is series or movies and title
        name match.
        :param data_title: name of title in netflix data
        :param series: True - title is series, False - title is movie
        :return: string of url of correct title
        """
        if self.response.status_code == 200:
            soup = BeautifulSoup(self.response.content, 'html.parser')
            if series:
                soup_section = soup.find_all("section", {"class": "box main-series"})
            else:
                soup_section = soup.find_all("section", {"class": "box main-movies"})
            for res in soup_section:
                soup_name = res.find_all("header", {"class": "article-header"})
                i = 0
                for name in soup_name:
                    title = name.find("p", {"class": "search-name"})
                    if title is None:
                        title = name.find("a", {"class": "film-title-name"})
                        title_str = title.text
                    else:
                        title_str = title.text
                        title_str = title_str.translate({ord(i): None for i in ')('})
                        if title_str != data_title:
                            title = name.find("a", {"class": "film-title-name"})
                            title_str = title.text
                    if title_str == data_title:
                        hrefs = res.find_all("a", {"class": "film-title-name"}, href=True)
                        link = hrefs[i].attrs['href']
                        return link
                    i += 1
                return None

    def scrape_actors(self, title: str, soup_film):
        """
        Scrapes tag soup_film for actors and saves result in scraped_table.
        :param title: title of movies or series that is currently scraped
        :param soup_film: tag with data to scrape
        :return: None
        """
        soup_creators = soup_film.find_all("h4")
        actors_arr = ''
        for creator in soup_creators:
            if creator.text == 'Hrají: ':
                actors = creator.parent.find_all("a", href=True)
                i = 0
                for actor in actors:
                    i += 1
                    actors_arr = actors_arr + actor.text
                    if i == 5:
                        break
                    actors_arr = actors_arr + ','
        self.scraped_table.loc[self.scraped_table.Title == title, 'Actors'] = actors_arr

    def scrape_film_page(self, title: str):
        """
        Scrapes from response data for film/series of name title. Call functions that find genre, years, rating,
            actors and country.
        :param title: title of movies or series that is currently scraped
        :return: None
         """

        if self.response.status_code == 200:
            soup = BeautifulSoup(self.response.content, 'html.parser')
            self.scrape_rating(title, soup)
            soup_film = soup.find("div", {"class": "film-info-content"})
            self.scrape_actors(title, soup_film)
            self.scrape_year_country(title, soup_film)
            self.scrape_genre(title, soup_film)
        else:
            print("Not found.")

    def start_scraping(self):
        """
        Scrapes in cycle all movies and series in table from csfd.
        :return: None
        """
        for title, series in zip(self.table.Title, self.table.Series):
            title_name = title.split(' ')
            self.response = self.session.get(self.base_url + self.search_url + '+'.join(title_name),
                                             headers=self.headers)
            title_url = self.scrape_search_page(title, series)
            time.sleep(0.75)
            if title_url is not None:
                self.response = self.session.get(self.base_url + title_url, headers=self.headers)
                self.scrape_film_page(title)
                time.sleep(1)

    def scrape_rating(self, title: str, soup_film):
        """
        Scrapes tag soup_film for rating and saves result in scraped_table.
        :param title: title of movies or series that is currently scraped
        :param soup_film: tag that has rating inside
        :return: None
        """
        soup_rating = soup_film.find("div", {"class": "rating-average"})
        rating = soup_rating.text.strip().translate({ord(i): None for i in '%'})
        try:
            self.scraped_table.loc[self.scraped_table['Title'] == title, 'Rating'] = int(float(rating))
        except ValueError:
            self.scraped_table.loc[self.scraped_table['Title'] == title, 'Rating'] = 50

    def scrape_year_country(self, title: str, soup_film):
        """
        Scrapes tag soup_film for year of start and end (for movies, the dates are same) and country that movies was
        made in and saves in scraped_table.
        :param title: title of movie/series
        :param soup_film: tag with data to scrape
        :return: None
        """
        soup_film = soup_film.find("div", {"class": "origin"})
        text_film = soup_film.text
        self.scraped_table.loc[self.scraped_table.Title == title, 'Country'] = text_film.split(',')[0]
        years = text_film.split(',')[1].translate({ord(i): None for i in ')( \n\t'})
        years = years.split('–')
        self.scraped_table.loc[self.scraped_table.Title == title, 'Year End'] = int(years[-1])
        self.scraped_table.loc[self.scraped_table.Title == title, 'Year Start'] = int(years[0])

    def scrape_genre(self, title, soup_film):
        """
        Scrapes tag soup_film for genres and saves in scraped_table.
        :param title: title of movies or series that is currently scraped
        :param soup_film: tag with data to scrape
        :return: None
        """
        genres = soup_film.find("div", {"class": "genres"})
        genre_arr = genres.text.split('/')
        genre_arr = ','.join(genre_arr).translate({ord(i): None for i in ' \n\t'})
        self.scraped_table.loc[self.scraped_table.Title == title, 'Genre'] = genre_arr

    def get_scraped_data(self):
        """
        :return: pandas table with scraped data
        """
        return self.scraped_table
