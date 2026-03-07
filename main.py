import os
from dotenv import load_dotenv
import requests 
import base64

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

def SPOTI_partse_album_json(album_json):
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

def SPOTI_get_album(album_url,access_token):
    album_id = album_url.split('/album/')[1].split('?')[0]
    response = requests.get(url= f'https://api.spotify.com/v1/albums/{album_id}',
                            headers={'Authorization': f'Bearer {access_token}'})
    if response.status_code != 200:
        print('Error:', response.status_code, response.text)
        return
    
    return SPOTI_partse_album_json(response.json())

if __name__ == '__main__':
    token = get_access_token()
    if token == None:
        print('No token')
    else:
        album = SPOTI_get_album('https://open.spotify.com/intl-es/album/791GBXI2YhfSdzn0ARQzlj',token)
        if album:
            print(f'Album: {album.name} - {album.artists}')
            for track in album.tracks:
                print(f'\tTrack {track.index}: {track.name}')