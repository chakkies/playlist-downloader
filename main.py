import asyncio
import time
import urllib
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, COMM, TCOM, TCON, TDRC, TRCK, APIC
from mutagen.easyid3 import EasyID3
from bs4 import BeautifulSoup
from pytube.exceptions import PytubeError
from ytmusicapi import YTMusic
from pytube import YouTube
from moviepy.editor import *
import threading
import requests
import json
import os
raplife = "https://music.apple.com/us/playlist/rap-life/pl.abe8ba42278f4ef490e3a9fc5ec8e8c5"
top100 = "https://music.apple.com/us/playlist/top-100-zimbabwe/pl.ad37160bb16c4c70a1d83d3670e96c1a"

# raplifeLocation = "C:\\Users\\Mchog\\Desktop\\RapLife"
# top100Location = "C:\\Users\\Mchog\\Desktop\\Top100 Zimbabwe"




header = f"{os.getcwd()}/header.json"
yt = YTMusic(header)

def delete_all_files(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")



async def getjson(url):
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    script = soup.script.string
    json_result = json.loads(script)
    return json_result


async def getPlayList(url):
    playlist = {}
    playlistJson = await getjson(url)


    for song in range(len(playlistJson["track"])):
        song_url = playlistJson["track"][song]["url"]
        songJson = await getjson(song_url)
        artist_name = songJson["audio"]["byArtist"][0]["name"]
        song_name = songJson["audio"]["name"]

        playlist[song_name] = artist_name
        # print(f'{song} {artist_name} {song_name}')
    return playlist

async def  download_song(title,artist,video_id,thumbnail,playlistlocation,track_nun,album):
    print(f"{track_nun} downloading {title}")
    link = f'https://music.youtube.com/watch?v={video_id}'
    filename = f"{title}.mp3"

    try:

        yt = YouTube(link)
        yt.title = "".join([c for c in yt.title if c not in ['/', '\\', '|', '?', '*', ':', '>', '<', '"']])
        video = yt.streams.filter(only_audio=True).first()
        vid_file = video.download(output_path=playlistlocation)
        base = os.path.splitext(vid_file)[0]
        audio_file = base + ".mp3"

        mp4_no_frame = AudioFileClip(vid_file)
        mp4_no_frame.write_audiofile(audio_file, logger=None)
        mp4_no_frame.close()
        os.remove(vid_file)
        os.replace(audio_file, playlistlocation + "/" + yt.title + ".mp3")
        audio_file = playlistlocation + "/" + yt.title + ".mp3"

        await set_song_metadata(title,artist,thumbnail,audio_file,track_nun,album)

    except PytubeError as e:
        print(f"An error occured while downloading: " + str(e))

async def get_song_metadata(song):
    results = yt.search(song, filter="songs")


    title = results[0]['title']
    album_name = results[0]['album']['name']
    artist = results[0]['artists'][0]['name']
    year = results[0]['year']
    video_id = results[0]['videoId']

    album = yt.get_album(results[0]["album"]["id"])
    url = album['thumbnails'][-1]['url']


    return title,artist,video_id,url

async def set_song_metadata(title,artist,thumbnail,location,track_num,album):
    print(f"setting metadata {title}")
    thumbnail = thumbnail
    mp3file = EasyID3(location)
    mp3file["albumartist"] = album
    mp3file["artist"] = artist
    mp3file["album"] = album
    mp3file["title"] = title
    mp3file["website"] = 't.me/mchoga'
    mp3file["tracknumber"] = str(track_num)
    mp3file.save()
    # self.track_num+=1

    audio = ID3(location)
    audio.save(v2_version=3)

    audio = ID3(location)
    with urllib.request.urlopen(thumbnail) as albumart:
        audio["APIC"] = APIC(
            encoding=3, mime="image/jpeg", type=3, desc="Cover", data=albumart.read()
        )
    audio.save(v2_version=3)



async def main(url, playlist_location,album):
    playlist = await getPlayList(url)

    # playlist = {'Bandit': 'Don Toliver', 'Mmhmm': 'BigXthaPlug', 'sneaky': '21 Savage', 'fukumean': 'Gunna', 'Patty Cake': 'Quavo', 'redrum': '21 Savage', 'Ocean Spray': 'Moneybagg Yo', 'HISS': 'Megan Thee Stallion'}
    count = 1
    for title, artist in playlist.items():
        x = await get_song_metadata(f"{artist} {title}")
        await download_song(x[0], x[1], x[2], x[3],playlist_location,count,album)
        count+=1
        print("meta data collected")



# asyncio.run(main(raplife,loc,"RapLife"))
# asyncio.run(main(raplife,raplifeLocation,"RapLife"))
# asyncio.run(main(top100,top100Location,"Top 100: Zimbabwe"))
# asyncio.run(main(raplife,"/app/music","Top 100: Zimbabwe"))

while True:
    asyncio.run(main(raplife, "/app/raplife", "RapLife"))
    asyncio.run(main(top100, "/app/top100", "Top 100: Zimbabwe"))
    time.sleep(604800)
    delete_all_files("/app/raplife")
    delete_all_files("/app/top100")





