from dotenv import load_dotenv
import os
import base64
from requests import post,get
import json
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect
import time

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    
    query = f"?q={artist_name}&type=artist&limit=1"
    
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("no artist with this name")
        return None
    return json_result[0]

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result


def get_user_playlist(token, user_id):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result


# def get_user_id(token):
#     url = f"https://api.spotify.com/v1/me"
#     headers = get_auth_header(token)
#     result = get(url, headers)
#     json_result = json.loads(result.content)
#     return json_result

def get_playlist(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)['tracks']['items']
    return json_result


def create_spotify_oauth():
    return SpotifyOAuth(client_id= client_id,
                        client_secret=client_secret,
                        redirect_uri= url_for("redirectpage", _external=True),
                        scope="user-library-read"
                        )

def get_user_token(TOKEN_INFO):
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    present = int(time.time())
    is_expired = token_info['expires_at'] - present < 60
    if (is_expired):
        sp_oauth = create_spotify_oauth()
        sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

def get_playlist_track_name(playlist):
    tracks = []
    for i in range(len(playlist)):
        tracks.append(playlist['items'][i]['track']['name'])
    return tracks
def get_playlist_track_artist(playlist):
    artist = []
    for i in range(len(playlist)):
        artistarray = (playlist['items'][i]['track']['artists'])
        
            
        artist.append(artistarray[0]['name'])
    return artist

def get_track_id(playlist):
    id = []
    for i in range(len(playlist)):
        id.append(playlist['items'][i]['track']['id'])
    return id


token = get_token()

# result =search_for_artist(token, "yoasobi")
# artist_id = result["id"]    

# songs = get_songs_by_artist(token,artist_id)

# for idx, song in enumerate(songs):
#     print(f"{idx + 1}. {song['name']} | {song['popularity']}")
    

#user_playlist = get_user_playlist(token, user_id)
# playlist_id = "0vlFkVxN2LIthqUeQQYbSj?si=784d9b5ae0e04a32"
# playlist = get_playlist(token, playlist_id)

# for idx,song in enumerate(playlist):
#     print(f"{idx + 1}. {song['track']['name']}")
