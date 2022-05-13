#!/usr/bin/env python

# Daniel Mendoza
# Robotics Engineer

import subprocess as sp
import sys
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pathlib import Path
home = str(Path.home())

spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

if (len(sys.argv) > 1):
    url = sys.argv[1]
else:
    url = None

if url:
    def get_song_by_url(spotify_share_url):
        spotify_share_url = spotify_share_url.rsplit('/')[-1].split('?')[0]
        results = spotify.track(spotify_share_url)
        track_dict = {
                'Preview Song URL': results['preview_url'],
                'Album Cover': results['album']['images'][0]['url'],
                'Album Name': results['album']['name'],
                'Artist': results['artists'][0]['name'],
                'Song': results['name'],
                }
        return track_dict

    result = get_song_by_url(url)
    SongURL = result['Preview Song URL']
    AlbumCover = result['Album Cover']
    Album = result['Album Name']
    Artist = result['Artist']
    Song = result['Song']
    print(f"""
    {'Album':<7}: {Album}
    {'Artist':<7}: {Artist}
    {'Song':<7}: {Song}
    """)
    downloaded_image = sp.Popen(
            ['wget', '-4', AlbumCover,
            '-O','album_cover','-q'
            ],stderr=sp.DEVNULL).communicate()
    play_preview_song = sp.Popen(
            ['xdg-open',SongURL],stderr=sp.DEVNULL).communicate()

    #time.sleep(2) #Please uncomment this line and modify the secs if necessary
    # If it depends on your internet speed and how fast the browser opens the
    # preview song url

    record_song = sp.Popen(
            ['ffmpeg','-y','-framerate','1','-i','album_cover',
            '-f','pulse','-i','default','-t','30','-vf','format=yuv420p',
            f'{home}/Videos/API_{Artist}_{Song}.mp4'
            ],stderr=sp.DEVNULL).communicate()
    sys.exit(0)

else:
    sys.stderr.write("[ERROR] - url not valid or not provided\n")
    sys.exit(1)
