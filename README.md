# Spotipy/ffmpeg python script to record a 30 secs song


This python script records a 30 sec song from your computer and downloads the album cover so you can use it to post on your favorite social media e.g. **"whatsapp status"** 📲 by default it will record your currently playing track.  
<br/>
You will need to create a developer app [Spotify Web API](https://developer.spotify.com/dashboard/) in order to access spotify related data.  
<br/>
Links:
- https://spotipy.readthedocs.io/en/2.19.0/#
- https://developer.spotify.com/dashboard/applications

**Prerequisites:**
- fmpeg version n5.0
- Python 3.10.4
- GNU Wget 1.21.3
- pulseaudio 15.0
- ImageMagick 7.0.8-11
- requirements.txt - python packages
```code
$ pip install -r requirements.txt
```

**OS:**
- **Arch Linux**
- Linux

## Usage:
By default will record your currently playing track.  
```code
$ python recording_spotify_track.py
```  
Passing **Spotify URI** will open the preview_song on your default browser and will be recorded.  
`-u <Spotify URI>, --url <Spotify URI>` 
```code
$ python recording_spotify_track.py --url <Spotify URI>
``` 

Passing **Spotify URI** **+** option `'cover'` or `'track'` will ither download the album cover or open the preview_song.   
`-o {'cover','track'}, --option {'cover','track'}`  
```code
$ python recording_spotify_track.py --url <Spotify URI> --option cover
```
```code
$ python recording_spotify_track.py --url <Spotify URI> --option track
```
<br>

**Spotify URI**  -> Copy Song Link

<img src="images/song_link.png" width="250">



