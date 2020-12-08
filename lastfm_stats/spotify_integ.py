import spotipy
import spotipy.util as util
import pandas as pd

'''
Spotify API Section

I wrote this section a while ago and failed to document, will investigate more but meantime will 
leave in this script
'''

username = 'Username_here'
token_grab_name = 'Grab_name_here' #<-- What are these for each

token = util.prompt_for_user_token(token_grab_name) #<-- currently this step doesn't work
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