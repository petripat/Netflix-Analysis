import copy
import pathlib
import streamlit as st
import pandas as pd
import sys
import re
from src.data_analysis import data_analysis


class DataLoad:

    def __init__(self):
        self.name = ""
        self.df = None

    def search_for_file(self, regex, file):
        if re.search(regex, file.name) is not None:
            return True
        return False

    def get_name(self):
        names = ['Select Name']
        names.extend(data_analysis.analyse_users(self.df))
        if len(names) == 1:
            st.error("No data") #todo
        else:
            option = st.selectbox(
            'Who are you?',
            names)
            self.name = option

    def check_structure(self, file):
        if self.search_for_file("ViewingActivity.csv*", file):
            self.df = pd.read_csv(file)
            if {'Profile Name', 'Start Time', 'Duration', 'Attributes', 'Title', 'Supplemental Video Type',
                'Device Type', 'Bookmark', 'Latest Bookmark', 'Country'}.issubset(self.df.columns):
                self.get_name()
                return True
        return False

# folders = ['netflix-report/MESSAGES/MessagesSentByNetflix.csv', 'netflix-report/CUSTOMER_SERVICE/CSContact.txt',
#            'netflix-report/CUSTOMER_SERVICE/ChatTranscripts.txt',
#            'netflix-report/CLICKSTREAM/Clickstream.csv',
#            'netflix-report/Cover sheet.pdf',
#            'netflix-report/PAYMENT_AND_BILLING/BillingHistory.csv',
#            'netflix-report/SURVEYS/ProductCancellationSurvey.txt',
#            'netflix-report/CONTENT_INTERACTION/PlaybackRelatedEvents.csv',
#            'netflix-report/CONTENT_INTERACTION/SearchHistory.csv',
#            'netflix-report/CONTENT_INTERACTION/Ratings.csv',
#            'netflix-report/CONTENT_INTERACTION/ViewingActivity.csv',
#            'netflix-report/CONTENT_INTERACTION/ViewingActivity.csv',
#            'netflix-report/CONTENT_INTERACTION/IndicatedPreferences.csv',
#            'netflix-report/CONTENT_INTERACTION/TastePreferences.txt',
#            'netflix-report/CONTENT_INTERACTION/MyList.csv',
#            'netflix-report/CONTENT_INTERACTION/InteractiveTitles.csv',
#            'netflix-report/PROFILES/ParentalControlsRestrictedTitles.txt',
#            'netflix-report/PROFILES/Profiles.csv',
#            'netflix-report/PROFILES/AvatarHistory.csv',
#            'netflix-report/DEVICES/Devices.csv',
#            'netflix-report/SOCIAL_MEDIA_CONNECTIONS/SocialMediaConnections.txt',
#            'netflix-report/Additional Information.pdf',
#            'netflix-report/IP_ADDRESSES/IpAddressesStreaming.csv',
#            'netflix-report/IP_ADDRESSES/IpAddressesLogin.csv',
#            'netflix-report/IP_ADDRESSES/IpAddressesAccountCreation.txt',
#            'netflix-report/ACCOUNT/SubscriptionHistory.csv',
#            'netflix-report/ACCOUNT/AccountDetails.csv',
#            'netflix-report/ACCOUNT/TermsOfUse.csv']
# data = DataLoad()
# data.set_files(folders)
# name = data.get_name()
# print(name)
# # data.set_name("Patricie")
# data.set_name("Daniel")
# # data.set_name("Dagmar")
# file = data.search_for_file('ViewingActivity.csv*')
# data_analysis.analyse_viewing_activity(file, data.name)
