import os
import re
import shutil
import string
import music_tag
import urllib.request
import pytubefix as pytube
from mutagen.mp3 import MP3
from pydub import AudioSegment
from ytmusicapi import YTMusic

ytmusic = YTMusic()
YOUTUBE_STREAM_AUDIO = '140'
def readconfs():
    with open("settings.conf", "r") as f:
        data = f.readlines()
        url = " "
        dir = " "

        for line in data:
            if line.split(" ")[0] == "URL":
                url = line.split(" ")[1].strip("\n")
            elif line.split(" ")[0] == "TARGET":
                dir = os.path.expanduser(line.split(" ")[1].strip("\n"))
        
        return url, dir
def sanitize_filename(filename: str) -> str:
    return re.sub(r'[^\w\s-]', '', filename).strip()

def convert_to_mp3(file_path: str) -> str:
    mp3_path = file_path.replace('.m4a', '.mp3')
    audio = AudioSegment.from_file(file_path, format="m4a")
    audio.export(mp3_path, format="mp3")
    os.remove(file_path)

    audio_file = MP3(mp3_path)
    audio_file.save()
    return mp3_path

def get_metadata(video_id: str):
    info = ytmusic.get_song(video_id)
    artist = info['videoDetails']['author']
    title = info['videoDetails']['title']
    return artist, title

def format_mp3(file_path: str, artist: str, title: str, thumbnail: str, download_dir) -> None:
    thumbpath = os.path.join(download_dir, "Thumb.jpg")
    urllib.request.urlretrieve(thumbnail, thumbpath)
    f = music_tag.load_file(file_path)
    f['album'] = title
    f['title'] = title
    f['artist'] = artist
    with open(thumbpath, 'rb') as i:
        f['artwork'] = i.read()
    f.save()
    os.remove(thumbpath)

class playlist:
    def __init__(self, url, download_dir):
        self.url = url
        self.plist = pytube.Playlist(self.url)
        self.plist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")
        self.download_dir = download_dir
    def download_videos(self):
        skip_count = 0
        download_count = 0
        for video in self.plist.videos:
            id = video.video_id
            thumbnail = video.thumbnail_url
            artist, title = get_metadata(id)
            sanitized=sanitize_filename(title)
            filename = sanitized + ".mp3"
            mp3_path = os.path.join(self.download_dir, filename)
            if not os.path.exists(mp3_path):
                print(f"Downloading {title}...", end='')
                audioStream = video.streams.get_by_itag(YOUTUBE_STREAM_AUDIO)
                path = audioStream.download(output_path=self.download_dir, filename=sanitized+".m4a")
                mp3_path = convert_to_mp3(path)
                format_mp3(mp3_path, artist, title, thumbnail, self.download_dir)
                print("Done.")
                download_count += 1
            else:
                print(f"Skipped Song {title} as it exists.")
                skip_count += 1
        print(f"{skip_count} songs skipped, {download_count} songs downloaded. Total {skip_count + download_count}")