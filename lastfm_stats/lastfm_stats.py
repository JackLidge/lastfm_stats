import datetime
import requests
import time
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

os.chdir('C:/Users/JackLidgley/Documents')

'''
Find file with authentications in it

Ensure that the file with Spotify & Last.fm authentications in it is in a subdirectory of the current Python
shell directory. Note that if you are searching through your entire filesystem, the find() function will
take a long time to execute.

Testing commit
'''
def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

name = 'Lastfm-Stats-Auth.txt'
path = os.getcwd()

authfile = find(name, path)
authframe = pd.read_csv(authfile,delimiter=',')


'''
Last.fm authentications
'''
key = authframe['key'][0]
username = authframe['username'][0]

'''
Spotify authentications
'''
os.environ["SPOTIPY_CLIENT_ID"] = authframe['spotipy_client_id'][0]
os.environ["SPOTIPY_CLIENT_SECRET"] = authframe['spotipy_client_secret'][0]
os.environ["SPOTIPY_REDIRECT_URI"] = authframe['spotipy_redirect_uri'][0]

pause_duration = 0.2

def get_scrobbles(method='recenttracks', username=username, key=key, limit=200, extended=0, page=1, pages=0):
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
    artist_names = []
    artist_mbids = []
    album_names = []
    album_mbids = []
    track_names = []
    track_mbids = []
    timestamps = []
    
    # make first request, just to get the total number of pages
    request_url = url.format(method, username, key, limit, extended, page)
    response = requests.get(request_url).json()
    total_pages = int(response[method]['@attr']['totalPages'])
    if pages > 0:
        total_pages = min([total_pages, pages])
        
    print('{} total pages to retrieve'.format(total_pages))
    
    # request each page of data one at a time
    for page in range(1, int(total_pages) + 1, 1):
        if page % 10 == 0: print(page, end=' ')
        time.sleep(pause_duration)
        request_url = url.format(method, username, key, limit, extended, page)
        responses.append(requests.get(request_url))
    
    # parse the fields out of each scrobble in each page (aka response) of scrobbles
    for response in responses:
        scrobbles = response.json()
        try:
            for scrobble in scrobbles[method]['track']:
                # only retain completed scrobbles (aka, with timestamp and not 'now playing')
                if 'date' in scrobble.keys():
                    artist_names.append(scrobble['artist']['#text'])
                    artist_mbids.append(scrobble['artist']['mbid'])
                    album_names.append(scrobble['album']['#text'])
                    album_mbids.append(scrobble['album']['mbid'])
                    track_names.append(scrobble['name'])
                    track_mbids.append(scrobble['mbid'])
                    timestamps.append(scrobble['date']['uts'])
        except KeyError:
            continue
                
    # create and populate a dataframe to contain the data
    df = pd.DataFrame()
    df['artist'] = artist_names
    df['artist_mbid'] = artist_mbids
    df['album'] = album_names
    df['album_mbid'] = album_mbids
    df['track'] = track_names
    df['track_mbid'] = track_mbids
    df['timestamp'] = timestamps
    df['datetime'] = pd.to_datetime(df['timestamp'].astype(int), unit='s')
    
    return df

scrobbles = get_scrobbles(pages=0)


        
'''
Data Gathered - Manipulation to create useful information
'''
crunched_data = pd.DataFrame(columns=['playlist','plays'])
year_scrobbles = scrobbles[(scrobbles['datetime'] > '2020-01-01') & (scrobbles['datetime'] < '2021-01-01')]
year_scrobbles = year_scrobbles.groupby(['artist','track', 'album']).count()
year_scrobbles = year_scrobbles.reset_index(level=['artist','track'])
for i in range(len(df)):
    playlist = df['playlist'].iloc[i]
    artist = df['artist'].iloc[i]
    track = df['track'].iloc[i]

    artist_scrobbles = year_scrobbles[year_scrobbles['artist'].str.match(artist)]
    
    if len(artist_scrobbles) == 0:
        number_of_plays = 0
#        print(track,artist,playlist)
    if len(artist_scrobbles) == 1:
        number_of_plays = artist_scrobbles.iloc[0]['artist_mbid']
    else:
        track_scrobbles = artist_scrobbles[artist_scrobbles['track'].str.match(track)]
        if len(track_scrobbles) == 0:
            number_of_plays = 0
            print(track,artist,playlist)
        else:
            number_of_plays = track_scrobbles.iloc[0]['artist_mbid']
    df1 = pd.DataFrame([[playlist,number_of_plays]],columns=['playlist','plays'])
    crunched_data = crunched_data.append(df1,ignore_index=True)
    
print(crunched_data.groupby('playlist')['plays'].sum())

dates = scrobbles['datetime'].map(pd.Timestamp.date).unique()
#dates = np.append(dates[:-1], datetime.date(2015, 4, 14))
for i, val in enumerate(scrobbles.iterrows()):
    scrobbles.loc[i, 'date'] = pd.Timestamp.date(scrobbles.loc[i, 'datetime'])
    if scrobbles.loc[i, 'date'] == datetime.date(1970, 1, 1):
        scrobbles.loc[i, 'date'] = datetime.date(2015, 4, 14)

def get_artist_plays(scrobbles, dates, name):
    artist_plays = []
    for i in dates[::-1]:
        day = scrobbles.loc[scrobbles['date'] == i]
        day_count = day.artist.str.count(name).sum()
        if len(artist_plays) == 0:
            artist_plays.append(day_count)
        else:
            day_count = artist_plays[-1] + day_count
            artist_plays.append(day_count)
    return artist_plays

artist_list = ['Mumford & Sons', "Bear's Den", 'Dire Straits', 'London Grammar', 'Oh Wonder']
#artist_list = ['Oh Wonder', 'Mumford & Sons', "Bear's Den", 'Kodaline', 'Everything Everything']
#artist_list = ['Twenty One Pilots', 'alt-J', 'Coldplay', 'Ludovico Einaudi', 'Hans Zimmer', 'Elbow']
fig, ax = plt.subplots(figsize=[9,6])
for artist in artist_list:
    y_vals = get_artist_plays(scrobbles, dates, artist)
    plt.plot(dates[::-1], y_vals, label=artist)
plt.legend()
plt.show()
