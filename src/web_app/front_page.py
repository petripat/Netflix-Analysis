import pathlib
import sys
import pandas
from pandas.core.base import DataError
import streamlit as st
from src.data_analysis import data_load, data_analysis
# For data netflix-report/CONTENT-INTRACTION/ViewingActivity.csv I already run scraping so I have data for testing
# purposes, it can be used with global_scrape_data = False and it shows page with large amount of data without scraping so
# it's fast.
# netflix-report/ViewingActivity.csv is very short version and that has to be only run with global_scrape_data = True

global_do_not_scrape = False

def print_error():
    """"Prints error returns None"""
    st.error("Data in file is not in correct format. Check that you uploaded file exactly as "
                             "received from Netflix.")


def run():
    """
    Main cycle of all program calls function for printing out data and analyzing. Scraping data is cached so if the name
    doesn't changes and it already ran, then it is fast otherwise scraping takes a while.
    :return: None
    """
    st.title("Let's analyse your Netflix data")
    st.info("Leave/Set light background color for better readability.")
    # st.write(sys.path)
    uploaded_file = st.file_uploader('Upload your netflix data', type='csv')
    a = st.radio("Do you need help with uploading data?", ['Yes', 'No'], 1)
    if a == 'No':
        pass
    else:
        st.write(
            "Download all your data from Netflix. Proccess is here: https://bitsabout.me/en/data-request-netflix/. Select "
            "from folders netflix-report/CONTENT_INTERACTION file ViewingActivity.csv and upload it here. ")
    data = data_load.DataLoad()
    if uploaded_file:
        if data.check_structure(uploaded_file):
            if data.name != 'Select Name':
                try:
                    data.df = data_analysis.prepare_data(data.df)
                    global global_do_not_scrape
                    if global_do_not_scrape:
                        scraped_data = data_analysis.select_scraped_data(data.name)
                    else:
                        scraped_data = data_analysis.add_scraped_data(data.df, data.name)
                    data_analysis.analyse_viewing_activity(data.name, data.df, scraped_data.copy())
                    data_analysis.title_data(scraped_data.copy())
                except DataError:
                        print_error()
                except ValueError:
                        print_error()
        else:
            print_error()

