# Spotipy/ffmpeg python script to record a 30 secs song


This python script records a 30 sec song from your computer and downloads the album cover so you can use it to post on your favorite social media e.g. **"whatsapp status"** 📲 by default it will record your currently playing track.  
<br/>
You will need to create a developer app [Spotify Web API](https://developer.spotify.com/dashboard/) in order to access spotify related data.  
<br/>
Links:
- https://spotipy.readthedocs.io/en/2.19.0/#
- https://developer.spotify.com/dashboard/applications

Tools requeired:
- fmpeg version n5.0
- Python 3.10.4
- GNU Wget 1.21.3
- pulseaudio 15.0
- ImageMagick 7.0.8-11
- requirements.txt - python packages


OS:
- Linux (**Arch Linux**)

## Usage:
```code
$ pip install -r requirements.tx

$ python recording_spotify_track.py
$ python recording_spotify_track.py -u <Spotify URI>
$ python recording_spotify_track.py -u <Spotify URI> -o cover
$ python recording_spotify_track.py -u <Spotify URI> -o track
$ python recording_spotify_track.py -o record
```

**Spotify URI** -> Copy Song Link

<img src="images/song_link.png" width="350">


