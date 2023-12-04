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

Valence_weight = 1
Energy_weight = 0.6
Danceability_weight = 0.4

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}



#helper functions

def create_spotify_oauth():
    return SpotifyOAuth(client_id= client_id,
                        client_secret=client_secret,
                        redirect_uri= url_for("redirectpage", _external=True),
                        scope="user-library-read user-top-read"
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




#mood calculation
def get_happy_value(valence_value, energy_value):
    Valence_weight = 0.7
    Energy_weight = 0.3
    happy_value = (Valence_weight * valence_value) + (Energy_weight * energy_value)
    
    return happy_value

def get_happy_value(valence_value, energy_value, danceability_value):
    Valence_weight = 0.5
    Energy_weight = 0.3
    Danceability_weight = 0.2
    
    happy_value = (Valence_weight * valence_value) + (Energy_weight * energy_value) \
        + (Danceability_weight * danceability_value) 
    
    return happy_value

def get_sad_value(valence_value, energy_value):
    Valence_weight = 0.7
    Energy_weight = 0.3
    sad_value = (Valence_weight * (1 - valence_value)) + (Energy_weight * (1 - energy_value))
    return sad_value

def get_sad_value(valence_value, energy_value, danceability_value):
    Valence_weight = 0.5
    Energy_weight = 0.3
    Danceability_weight = 0.2
    
    sad_value = 1 - ((Valence_weight * valence_value) + (Energy_weight * energy_value) \
        + (Danceability_weight * danceability_value))
    
    return sad_value

def get_calm_value(danceability_value, energy_value):
    Danceability_weight = 0.2
    Energy_weight = 0.2
    calm_value = (Danceability_weight * (1 - danceability_value)) + (Energy_weight * energy_value)
    
    return calm_value

def get_calm_value(danceability_value, energy_value, valence_value, instrumentalness_value):
    Danceability_weight = 0.2
    Energy_weight = 0.2
    Valence_weight = 0.35
    Instrumentalness_weight = 0.25
    
    calm_value = (Danceability_weight * (1 - danceability_value)) + (Energy_weight * (1 - energy_value)) \
            + (Valence_weight * (1 - valence_value)) +  \
            + (Instrumentalness_weight * (1 - instrumentalness_value))
            
    return calm_value


def get_energetic_value(danceability_value, energy_value):
    Danceability_weight = 0.3
    Energy_weight = 0.3
    
    energetic_value = (Danceability_weight * danceability_value) + (Energy_weight * energy_value)
    
    return energetic_value

def get_energetic_value(danceability_value, energy_value, valence_value, instrumentalness_value):
    Danceability_weight = 0.35
    Energy_weight = 0.35
    Valence_weight = 0.2
    Instrumentalness_weight = 0.1
    
    energetic_value = (Danceability_weight * danceability_value) + (Energy_weight * energy_value) \
            + (Valence_weight * valence_value) +  \
            + (Instrumentalness_weight * instrumentalness_value)
            
    return energetic_value

