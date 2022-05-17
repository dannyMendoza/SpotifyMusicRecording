#!/usr/bin/env python

# Daniel Mendoza
# Robotics Engineer

import argparse
import subprocess as sp
import sys
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials,SpotifyOAuth
from pathlib import Path
home = str(Path.home())


scope = """
user-read-playback-state,
user-read-currently-playing,
user-modify-playback-state
"""

# Enable access to read and modify playback state
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
#spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

to_do = ['cover','track','record']
parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=f'''
Access to user related data from spotify and record a 30 secs track
-------------------------------------------------------------------

Short option description:

[playing] default : Will record currently playing track
[cover]           : Download cover album - "Spotify URI" required
[track]           : Preview song - "Spotify URI" required
[record]          : Record 30 secs from your computer audio
        ''')
parser.add_argument('-o', '--option', type=str, choices=to_do,
        default='playing', required=False,
        help='[option]')
parser.add_argument('-u','--url', type=str, default='playing',
        help="[url]")
parser.add_argument('-v', '--version', action='version', version='%(prog)s v1.1')

args = parser.parse_args()
url = args.url
option = args.option

# Check if spotify is active
def spotify_state():
    device_id = None
    devices = spotify.devices()['devices']
    for device in devices:
        if device['is_active']:
            device_id = device['id']
            print(f"\n    Active device: {device['name']}")
            break
    return device_id

# Validate arguments and get playback data accordingly
def get_song_by_url(url,option):
    if (option in ('cover','track') and url == 'playing'):
            sys.stderr.write(f"[ERROR] - Required url\n")
            sys.exit(1)
    if option == 'record':
        # This option will record what your are playing on your computer
        # Current Album folder will be used
        # Please consider that album_cover size must be 640x640
        Artist = input(f"""\n    Enter Artist name: """)
        Song = input(f"    Song name: ")
        print()
        return Artist, Song
    elif url != 'playing':
        # Get track id from Spotify URI
        url = url.rsplit('/')[-1].split('?')[0]
        results = spotify.track(url)
    else:
        if not spotify_state():
            sys.stderr.write(f"[ERROR] - Spotify is not running\n")
            sys.exit(3)
        results = spotify.current_user_playing_track()
        results = results['item']
    track_dict = {
            'Preview Song URL': results['preview_url'],
            'Album Cover': results['album']['images'][0]['url'],
            'Album Name': results['album']['name'],
            'Artist': results['artists'][0]['name'],
            'Song': results['name'],
            }
    return track_dict


result = get_song_by_url(url, option)

if isinstance(result,tuple):
    (Artist,Song) = result
else:
    SongURL = result['Preview Song URL']
    AlbumCover = result['Album Cover']
    Album = result['Album Name']
    Artist = result['Artist']
    Song = result['Song']


# OUTPUT
def print_to_terminal():
    data = f"""

        {'Album':<7}: {Album}
        {'Artist':<7}: {Artist}
        {'Song':<7}: {Song}

    """
    return data


# Get album cover - wget and imagemagick required
def cover():
    cover_pic = sp.Popen(
            ['wget', '-4', AlbumCover,
            '-O','album_cover','-q'
            ], stdout=sp.PIPE, stderr=sp.DEVNULL).communicate()[0]
    # Validate if the size of the album cover is 640x640
    # if the size is different it will be changed to 640x640
    image_size1 = sp.Popen(
            ['file', 'album_cover'], stdout=sp.PIPE)
    image_size2 = sp.Popen(
            ["awk {'print $18'}"],
            shell=True, stdin=image_size1.stdout, stdout=sp.PIPE)
    image_size1.stdout.close()
    image_size3 = sp.Popen(
            ['tr', '-d', '\,'],
            text=True, stdin=image_size2.stdout, stdout=sp.PIPE, stderr=sp.PIPE)
    image_size2.stdout.close()
    image = image_size3.communicate()[0]
    if image != '640x640':
        convert = sp.Popen(
                ['convert', 'album_cover', 
                    '-resize', '640x640!', 'album_cover'],
                stdout=sp.PIPE,
                stderr=sp.DEVNULL)
        convert.communicate()[0]
    return cover_pic

# Play track preview on your default browser 
def track():
    track =  sp.Popen(
            ['xdg-open',SongURL],stdout=sp.PIPE, stderr=sp.DEVNULL)
    return track.communicate()


# Record ("30" secs) audio from your computer 
def record():
    recorded = sp.Popen(
            ['ffmpeg','-y','-framerate','1','-i','album_cover',
            '-f','pulse','-i','default','-t','30','-vf','format=yuv420p',
            f'{home}/Videos/API_{Artist}_{Song}.mp4'
            ],stdout=sp.PIPE, stderr=sp.DEVNULL)

    return recorded.communicate()


def check():
    it_was_playing = False
    if args.url != 'playing':
        if option != 'playing':
            return 1
        print(print_to_terminal())
        for o in to_do:
            if o == 'record' and spotify.currently_playing()['is_playing']:
                spotify.pause_playback()
                it_was_playing = True
                # Modify time.sleep(1) secs if necessary, it depends on your 
                # internet speed and how fast the browser starts playing 
                # ("preview_url") track.
                time.sleep(1)
            eval(o + '()')
        if it_was_playing:
            spotify.start_playback()
        print(f"    ⏺️  Song recorded successfully\n")
        return 0
    return 1


if check():
    if (option == 'playing'):
        print(print_to_terminal())
        for o in to_do:
            if o == 'track':
                continue
            if o == 'record' and not spotify.currently_playing()['is_playing']:
                spotify.start_playback()
            eval(o + '()')
        print(f"    ⏺️  Song recorded successfully\n")
    elif (option == 'cover'):
        print(print_to_terminal())
        eval(option + '()')
        print(f"    🖼️  Cover '{Album}' downloaded successfully!\n")
    elif (option == 'record'):
        # cover()
        counter = 3
        while counter > 0:
            print(f"    Recording in {counter}")
            counter -= 1
            time.sleep(1)
        print()
        eval(option + '()')
        print(f"    ⏺️  Song recorded successfully\n")
    else:
        if spotify.currently_playing()['is_playing']:
            spotify.pause_playback()
        print(print_to_terminal())
        eval(option + '()')
        print(f"    🔊 I hope you enjoy '{Song}' track\n")

print(f"    Thanks for using this 🐍 script\n")
