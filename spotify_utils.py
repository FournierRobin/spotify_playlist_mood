import requests
import os
from dotenv import load_dotenv

AUTH_URL = 'https://accounts.spotify.com/api/token'
BASE_URL = 'https://api.spotify.com/v1/'

def authenticate_to_spotify():
    """Authenticate to Spotify API and return headers with access token."""
    load_dotenv()

    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')

    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })

    auth_response_data = auth_response.json()
    access_token = auth_response_data['access_token']
    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }
    return headers

def get_songs_based_on_mood_data(mood_data, headers):
    """Fetch recommended songs from Spotify API based on mood data."""
    request_url = (BASE_URL + 'recommendations?limit=10'
                   '&seed_genres=' + mood_data.get('genre', 'pop') +
                   '&target_acousticness=' + str(mood_data.get('target_acousticness', 0.5)) +
                   '&target_danceability=' + str(mood_data.get('target_danceability', 0.5)) +
                   '&target_energy=' + str(mood_data.get('target_energy', 0.5)) +
                   '&target_instrumentalness=' + str(mood_data.get('target_instrumentalness', 0.5)) +
                   '&target_speechiness=' + str(mood_data.get('target_speechiness', 0.5)))
    
    recommendations = requests.get(request_url, headers=headers)
    tracks = recommendations.json().get('tracks', [])
    
    songs = []
    for track in tracks:
        song_details = {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'url': track['external_urls']['spotify']
        }
        songs.append(song_details)
    
    return songs