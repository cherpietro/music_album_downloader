import os
from dotenv import load_dotenv
import requests 
import base64
import yt_dlp
import sys   

clear = lambda: os.system('clear')

load_dotenv()
client_id=os.getenv('CLI_ID')
client_secret=os.getenv('CLI_SC')
client_credentials = base64.b64encode(bytes(f'{client_id}:{client_secret}', 'utf-8')).decode('utf-8')

class Track:
    def __init__(self,name,index,duration):
        self.name = name
        self.index = index
        self.duration = duration

class Album:
    def __init__(self, name, cover_url, artists):
        self.name = name    
        self.cover_url = cover_url  
        self.artists = artists  
        self.tracks = []
    def add_track(self,track):
        self.tracks.append(track)
        
def get_access_token():
    try:
        response = requests.post(url='https://accounts.spotify.com/api/token',
                             headers={'Authorization': f'Basic {client_credentials}'},
                             data={'grant_type': 'client_credentials','json': 'true'}).json()
        return response['access_token']
    except:
        return None

def SPOTI_parse_album_json(album_json):
    biggest_image_width = 0 
    album_img_url = ''
    for image in album_json['images']:
        if biggest_image_width < image['width']:
            album_img_url = image['url']
            biggest_image_width = image['width']

    album_name = album_json['name']

    album_artists = ''
    for artist in album_json['artists']:
        if album_artists == '': album_artists = artist['name']
        else: album_artists += f',{artist['name']}'

    album = Album(name=album_name,cover_url=album_img_url,artists=album_artists)
    for track in album_json['tracks']['items']:
        album.add_track(Track(name=track['name'],index=track['track_number'],duration=track['duration_ms']))

    return album

def SPOTI_search_album(album_url,access_token):
    album_id = album_url.split('/album/')[1].split('?')[0]
    response = requests.get(url= f'https://api.spotify.com/v1/albums/{album_id}',
                            headers={'Authorization': f'Bearer {access_token}'})
    if response.status_code != 200:
        print('Error:', response.status_code, response.text)
        return
    
    return SPOTI_parse_album_json(response.json())

def SPOTY_search_album_uri_by_name(access_token):
    print('enter album name to seach on spotify:')
    query = input()
    
    response = requests.get(url= f'https://api.spotify.com/v1/search?q={query}&type=album',
                        headers={'Authorization': f'Bearer {access_token}'})
    if response.status_code != 200:
        print('Error:', response.status_code, response.text)
        return None
    
    clear()
    print('--------------Albums found--------------')
    query_results = response.json()
    for index, album in enumerate(query_results['albums']['items']):
        album_artists = ''
        for artist in album['artists']:
            if album_artists == '': album_artists = artist['name']
            else: album_artists += f',{artist['name']}'
            
        print(f'{index} - {album['name']} | {album_artists}')
    try:
        index = int(input("Enter the index of the desired album: "))
        if  index >= len(query_results['albums']['items']) or index < 0:
            print("Invalid index.")
            return None
    except ValueError:
        print("Invalid index.")
        return None
    
    clear()
    return query_results['albums']['items'][index]['uri'].split(':')[2]
import textwrap

def YD_DLP_get_titles(url):
    album = []
    ydl_opts = {
        # "quiet": True,
        'outtmpl': '%(playlist_title)s/%(title)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best', 
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }
        ],
        'noplaylist': False, 
        # 'cookiesfrombrowser': ('firefox',)   #only for windows 
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist_dict = ydl.extract_info(url, download=False)

        for video in playlist_dict["entries"]:
            if not video:
                print("ERROR: Unable to get info. Continuing...")
            else:
                album.append({"title":str(video.get("title")),
                                "duration":str(video.get("duration"))})
    return album
def get_spotify_album():
    token = get_access_token()
    if token == None:
        print('No token')
    else:
        album_uri = SPOTY_search_album_uri_by_name(token)
        if album_uri == None:
            return None
        album_url = f'https://open.spotify.com/intl-es/album/{album_uri}'
        album = SPOTI_search_album(album_url,token)

        return album
    
import unicodedata
def clean_text(s):
    s = unicodedata.normalize("NFKC", s)
    s = s.strip()
    s = " ".join(s.split())
    return s

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python main.py <youtube_url>") 
        sys.exit(1) 

    if not sys.argv[1].startswith("https://www.youtube.com"):
        print("Not youtube url") 
        sys.exit(1) 
    if not "list" in sys.argv[1]:
        print("Not list url") 
        sys.exit(1) 
    album = get_spotify_album()
    if album == None:
        sys.exit(1) 
        
    ytAlbum = YD_DLP_get_titles(sys.argv[1])
    clear()
    if len(ytAlbum) == len(album.tracks):
        match = 0
        for index, _ in enumerate(ytAlbum):
            if clean_text(album.tracks[index].name.lower()) in clean_text(ytAlbum[index]['title'].lower()): match+=1
            print(f'{(ytAlbum[index]['title'].lower())} | {album.tracks[index].name.lower()};',end='')
            print(f'{clean_text(album.tracks[index].name.lower()) in clean_text(ytAlbum[index]['title'].lower())}')
        if match/len(ytAlbum) > 0.5:
            print('ID3 TAGS SHOULD BE CORRECT')
            sys.exit(0) 
    print('ID3 TAGS ARE NOT CORRECT')

