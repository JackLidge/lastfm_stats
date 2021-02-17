# lastfm-stats

[![Downloads](https://pepy.tech/badge/lastfm-stats)](https://pepy.tech/project/lastfm-stats)

A package which gathers a users scrobbles from Last.fm.

Requires a text file with the username and API key in the following format:

```
key,username
**\API key**,**\username**
```

The package can then be initialised like so:

`lastfm_obj = lastfm_stats.lastfm()`

The credentials for accessing a users scrobbles added to the object with:

`lastfm_obj.get_credentials(path='path_to_file')`

And finally the scrobbles read using:

`lastfm_obj.get_scrobbles()`