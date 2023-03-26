#!/usr/bin/env python

# Daniel Mendoza
# Robotics Engineer

import argparse
import time
import os
import re
import subprocess as sp
import sys
import spotipy
import socket
from pathlib import Path


videos = str(Path.home()) + '/Music/'
pics = str(Path.home()) + '/Documents/GITREPOS/music.dmweb/images/'
script_path = str(Path(__file__).parent.absolute()) + '/'
file = str(Path.home()) + '/Documents/GITREPOS/music.dmweb/Melodies.txt'
sp.run(f'rm -f {script_path}*.mp4',shell=True,stdout=sp.DEVNULL)
sp.run(f'rm -f {script_path}*.png',shell=True,stdout=sp.DEVNULL)
hostname = socket.gethostname()
audio_sources = sp.Popen(['pactl','list','short','sources'],
                         stdout=sp.PIPE,stderr=sp.PIPE,text=True
                         ).communicate()[0].strip()
audio_ouput = re.search(r'(?<=\s)alsa_output[^\s]+',audio_sources).group(0)

scope = '''
user-read-playback-state,
user-read-currently-playing,
user-modify-playback-state
'''

# Enable access to read and modify playback state
with open(f'{script_path}.username','r') as hidden:
    username = hidden.readline().strip('\n')

token = spotipy.util.prompt_for_user_token(username, scope)
spotify = spotipy.Spotify(token)

to_do = ['cover','track','record','mpqtile']
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
[mscplayer]       : Personal consumed from musicplayer Qtile :)
        ''')

parser.add_argument('-o', '--option', type=str, choices=to_do,
        default='playing', required=False,
        help='[option]')
parser.add_argument('-u','--url', type=str, default='playing',
        help="[url]")
parser.add_argument('-v', '--version', action='version', version='%(prog)s v1.2')

args = parser.parse_args()
url = args.url
option = args.option

def is_playing():
    try:
        playing = spotify.currently_playing()['is_playing']
        if playing:
            return 1
    except TypeError:
        # This exception is thrown only in case spotify is active 
        # but nothing has been played
        return 2
    return 0


# Check if spotify is active
def spotify_state():
    device_id = None
    devices = spotify.devices()['devices']
    for device in devices:
        device_type = device['type']
        if device_type != 'Smartphone':
            if args.option == 'mpqtile':
                return f"{device['name']} {is_playing()}"
            device_id = device['id']
            if is_playing == 2:
                spotify.start_playback(device_id)
                time.sleep(1)
            print(f"\n    Active device: {device['name']}")
            break
        else:
            try:
                if device['name'].startswith('Web'):
                    device_id = device['id']
                    spotify.start_playback(device_id)
            except:
                print('Spotify not active')
    return device_id

# Only used from qtilescripts/musicplayer.py
if args.option == 'mpqtile':
    def mp():
        print(spotify_state())
    mp()
    sys.exit()


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
        if not device_id:
            sys.stderr.write(f"[ERROR] - Spotify is not running in this device\n")
            sys.exit(3)
        while True:
            results = spotify.current_user_playing_track()
            if results:
                results = results['item']
                break
    track_dict = {
            'Preview Song URL': results['preview_url'],
            'Album Cover': results['album']['images'][0]['url'],
            'Album Name': results['album']['name'],
            'Artist': results['artists'][0]['name'],
            'Song': results['name'],
            'URL': results['external_urls']['spotify']
            }
    return track_dict


# OUTPUT
def print_to_terminal():
    data = f"""

        {'Album':<7}: {Album}
        {'Artist':<7}: {Artist}
        {'Song':<7}: {Song}
        {'URL':<7}: {URL}

    """
    return data


# Get album cover - wget and imagemagick required
def cover():
    cover_pic = sp.Popen(
            ['wget', '-4', AlbumCover,
            '-O',f'{script_path}album_cover','-q'
            ], stdout=sp.PIPE, stderr=sp.DEVNULL).communicate()[0]
    # Validate if the size of the album cover is 640x640
    # if the size is different it will be changed to 640x640
    image_size1 = sp.Popen(
            ['file', f'{script_path}album_cover'], stdout=sp.PIPE)
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
                ['convert', f'{script_path}album_cover', 
                    '-resize', '640x640!', f'{script_path}album_cover'],
                stdout=sp.PIPE,
                stderr=sp.DEVNULL)
        convert.communicate()[0]
    return cover_pic

# Play track preview on your default browser 
def track():
    track =  sp.Popen(
            ['xdg-open',SongURL],stdout=sp.PIPE, stderr=sp.DEVNULL)
    return track.communicate()

# Check if the track already exists
def mp4_exists(track):
    counter = 0
    track_exists = Path(track)
    while track_exists.is_file():
        counter += 1
        track = f'{videos}{Artist} : {Album} : {Song}_{counter}.mp4'
        track_exists = Path(track)
    return track

# Record ("30" secs) audio from your computer 
def record():
    recorded = sp.Popen(
            ['ffmpeg','-y','-framerate','1','-i',f'{script_path}album_cover',
             '-f','pulse','-i',audio_ouput,
             '-metadata',f'artist={Artist}',
             '-metadata',f'album={Album}',
             '-metadata',f'title={Song}',
             '-t','30','-vf','format=yuv420p',
             '-af','afade=t=out:st=25:d=5',video_recorded],
            stdout=sp.PIPE, stderr=sp.PIPE)

    return recorded.communicate()

def add_thumbnail(video,image):
    thumb = sp.Popen(
            ['ffmpeg','-y','-i',video,
             '-vf',"thumbnail,scale=320:320",
             '-frames:v','1',image,],
            stdout=sp.PIPE,stderr=sp.DEVNULL)
    thumb.communicate()[0]

    mv_to_pics = sp.Popen(
            ['cp','-f',f'{image}',f'{pics}'],stdout=sp.PIPE, stderr=sp.DEVNULL)
    mv_to_pics.communicate()[0]

    thumbnailed = sp.Popen(
            ['ffmpeg','-y','-i',video,'-i',image,
                '-map','1','-map','0','-c','copy','-disposition:0','attached_pic',
                f'{track_output}'
            ],stdout=sp.PIPE, stderr=sp.DEVNULL)

    return thumbnailed.communicate()


utf_fwdslasah = "\U00002044"
is_playing = is_playing()
device_id = spotify_state()
result = get_song_by_url(url, option)

if isinstance(result,tuple):
    (Artist,Song,Album) = result
else:
    SongURL = result['Preview Song URL']
    AlbumCover = result['Album Cover']
    Album = result['Album Name'].replace("/",f"{utf_fwdslasah}")
    Artist = result['Artist'].replace("/",f"{utf_fwdslasah}")
    Song = result['Song'].replace("/",f"{utf_fwdslasah}")
    URL = result['URL']

# txt file that enables records the URL
def write_to_txt():
    with open(file,'r+') as txt:
        for line in txt.readlines():
            if f'{Album} : {Song} : {URL}' in line:
                return
        txt.write(f'{Album} : {Song} : {URL}\n')
write_to_txt()

track_playing = f'{videos}{Artist} : {Album} : {Song}.mp4'
video_recorded = f'{script_path}{Artist} : {Album} : {Song}.mp4'
thumbnail_image = f'{script_path}{Album}.png'
track_output = mp4_exists(track_playing)

def check():
    it_was_playing = False
    if args.url != 'playing':
        if option != 'playing':
            return 1
        print(print_to_terminal())
        for o in to_do:
            if o == 'mpqtile':
                continue
            if o == 'record' and is_playing:
                spotify.pause_playback()
                it_was_playing = True
                # Modify time.sleep(1) secs if necessary, it depends on your 
                # internet speed and how fast the browser starts playing 
                # ("preview_url") track.
                time.sleep(1)
            eval(o + '()')
        if it_was_playing:
            spotify.start_playback()
        print(f"    ⏺️  Song successfully recorded\n")
        add_thumbnail(video_recorded,thumbnail_image)
        return 0
    return 1


if check():
    if (option == 'playing'):
        print(print_to_terminal())
        for o in to_do:
            if o == 'track' or o == 'mpqtile':
                continue
            if o == 'record' and not is_playing:
                spotify.start_playback()
            eval(o + '()')
        print(f"    ⏺️  Song recorded successfully\n")
        add_thumbnail(video_recorded,thumbnail_image)
    elif (option == 'cover'):
        print(print_to_terminal())
        eval(option + '()')
        print(f"    🖼️  Cover '{Album}' downloaded successfully!\n")
    elif (option == 'record'):
        counter = 3
        while counter > 0:
            print(f"    Recording in {counter}")
            counter -= 1
            time.sleep(1)
        eval(option + '()')
        print(f"    ⏺️  Song recorded successfully\n")
        add_thumbnail(video_recorded,thumbnail_image)
    else:
        if is_playing:
            spotify.pause_playback()
        print(print_to_terminal())
        eval(option + '()')
        print(f"    🔊 I hope you enjoyed '{Song}' track\n")

print(f"    Thanks for using this 🐍 script\n")
