import datetime
import os
import time
import sys
import requests
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class lastfm():
    
    def __init__(self):
        self.user = os.getlogin()
        
    def get_credentials(self, path='Default Path'):
        '''
        Add docstring here
        '''
        
        def find(name, path):
            for root, dirs, files in os.walk(path):
                if name in files:
                    return os.path.join(root, name)

        if path == 'Default Path':
            raise KeyError('Please specify a path to the Lastfm authentication folder')
        print(os.path.isabs(path))
        if os.path.isabs(path) == False:
            if sys.platform == 'win32':
                self.authfile = find(path, os.path.join('C:/', 'Users', self.user))
            elif sys.platform == 'linux':
                self.authfile = find(path, os.path.join('/', 'home', self.user))
        else:
            self.authfile = path
        
        try:
            self.authframe = pd.read_csv(self.authfile,delimiter=',')
        except ValueError:
            raise FileNotFoundError('Cannot find file with Lastfm authentication')
        
        
    def get_scrobbles(self, method='recenttracks', limit=200, extended=0, page=1, pages=0, 
                      pause_duration=0.2):
        '''
        method: api method
        username/key: api credentials
        limit: api lets you retrieve up to 200 records per call
        extended: api lets you retrieve extended data for each track, 0=no, 1=yes
        page: page of results to start retrieving at
        pages: how many pages of results to retrieve. if 0, get as many as api can return.
        '''
        # initialize url and lists to contain response fields
        url = 'https://ws.audioscrobbler.com/2.0/?method=user.get{}&user={}&api_key={}&limit={}&extended={}&page={}&format=json'
        responses = []
        
        key = self.authframe['key'][0]
        username = self.authframe['username'][0]
        
        # make first request, just to get the total number of pages
        request_url = url.format(method, username, key, limit, extended, page)
        response = requests.get(request_url).json()
        total_pages = int(response[method]['@attr']['totalPages'])
        if pages > 0:
            total_pages = min([total_pages, pages])
                    
        # request each page of data one at a time
        for page in range(int(total_pages) + 1):
            if page % 10 == 0:
                print(f'\r{round(page / total_pages * 100, 2)}% of pages requested', end='')
            elif page == total_pages:
                print('\r100% of pages requested', end='')
            time.sleep(pause_duration)
            request_url = url.format(method, username, key, limit, extended, page)
            responses.append(requests.get(request_url))
            
        scrobble_list = []
        # parse the fields out of each scrobble in each page (aka response) of scrobbles
        for response in responses:
            scrobbles = response.json()
            try:
                for scrobble in scrobbles[method]['track']:
                    # only retain completed scrobbles (aka, with timestamp and not 'now playing')
                    if 'date' in scrobble.keys():
                        temp = {'artist_name': scrobble['artist']['#text'],
                                'artist_mbids': scrobble['artist']['mbid'],
                                'album_names': scrobble['album']['#text'],
                                'album_mbids': scrobble['album']['mbid'],
                                'track_names': scrobble['name'],
                                'track_mbids': scrobble['mbid'],
                                'timestamp': scrobble['date']['uts']
                               }
                        scrobble_list.append(temp)
            except KeyError:
                continue
                    
        # create and populate a dataframe to contain the data
        self.scrobbles = pd.DataFrame(scrobble_list)
        self.scrobbles['datetime'] = pd.to_datetime(self.scrobbles['timestamp'].astype(int), unit='s')
        
    def plot_scrobbles_over_time(self, bands, savefig=None):
        '''
        Add docstring here
        '''
        def get_artist_plays(scrobbles, dates, name):
            artist_plays = []
            for i in dates[::-1]:
                day = scrobbles.loc[scrobbles['date'] == i]
                day_count = day.artist_name.str.count(name).sum()
                if len(artist_plays) == 0:
                    artist_plays.append(day_count)
                else:
                    day_count = artist_plays[-1] + day_count
                    artist_plays.append(day_count)
            return artist_plays
        
        # Search for errored scrobble dates (pre lastfm existing), remove them and create new day 
        # for them before first scrobble.
        dates = self.scrobbles['datetime'].map(pd.Timestamp.date).unique()
        correct_dates = [i for i in dates if i > datetime.date(2002, 1, 1)]
        if len(dates) != len(correct_dates):
            dates = dates.sort()
            dates = np.append(dates, datetime.date(dates[-1].year, dates[-1].month, dates[-1].day-1))

        # Converts the pandas timestamp to a datetime date object
        for i, val in enumerate(self.scrobbles.iterrows()):
            self.scrobbles.loc[i, 'date'] = pd.Timestamp.date(self.scrobbles.loc[i, 'datetime'])
            if self.scrobbles.loc[i, 'date'] < datetime.date(2002, 1, 1):
                self.scrobbles.loc[i, 'date'] = datetime.date(dates[-1].year, dates[-1].month, dates[-1].day-1)
                
        fig, ax = plt.subplots(figsize=[9,6])
        if isinstance(bands, list) == True:
            for band in bands:
                y_vals = get_artist_plays(self.scrobbles, dates, band)
                plt.plot(dates[::-1], y_vals, label=band)
        else:
            y_vals = get_artist_plays(self.scrobbles, dates, bands)
            plt.plot(dates[::-1], y_vals, label=band)
        plt.legend()
        plt.xlabel('Date')
        plt.ylabel('Scrobbles')
        if savefig:
            plt.savefig(savefig, dpi=300)
        plt.show()
