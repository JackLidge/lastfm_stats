import requests
import time
import pandas as pd
import os
import spotipy
import spotipy.util as util

'''
Last.fm authentications
'''
key = '53fe696d9a2a99714a824e4d8c063fa5'
username = 'JackLidge'

'''
Spotify authentications
'''
os.environ["SPOTIPY_CLIENT_ID"] = 'ab092841c2b44c06be11dd4e2b812966'
os.environ["SPOTIPY_CLIENT_SECRET"] = '84fdc7267c2441379ad2e1a61dbc83fe'
os.environ["SPOTIPY_REDIRECT_URI"] = 'https://github.com/JackLidge/Lastfm-Stats'

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

# sort dataframe by datetime
# scrobbles[scrobbles['datetime'] > '2018-01-01']

# sort dataframe by artist plays
# scrobbles['artist'].value_counts()

# sort dataframe by artist & track
# scrobbles.groupby(['artist','track']).count()

'''
Spotify API Section
'''

username = 'jacklidgley95'

token = util.prompt_for_user_token(username)
sp = spotipy.Spotify(auth=token)
playlists = sp.user_playlists(username)

def show_tracks(results,playlist_name,df):
    for i, item in enumerate(results['items']):
        track = item['track']
        df1 = pd.DataFrame([[playlist_name,track['artists'][0]['name'],track['name']]],\
                           columns=['playlist','artist','track'])
        df = df.append(df1,ignore_index=True)
    return df
df = pd.DataFrame(columns=['playlist','artist','track'])

for playlist in playlists['items']:
    if playlist['owner']['id'] == username:
        print("%d tracks: %s" % (playlist['tracks']['total'],playlist['name']))
        results = sp.user_playlist(username,playlist['id'],fields='tracks,next')
        df = show_tracks(results['tracks'],playlist['name'],df)
        
'''
Data Gathered - Manipulation to create useful information
'''
crunched_data = pd.DataFrame(columns=['playlist','plays'])
year_scrobbles = scrobbles[scrobbles['datetime'] > '2018-01-01' & scrobbles['datetime'] < '2019-01-01']
year_scrobbles = year_scrobbles.groupby(['artist','track']).count()
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