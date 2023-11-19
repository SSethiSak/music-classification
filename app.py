from flask import Flask, request, url_for, session, redirect,render_template
import spotipy
import helper
import os
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import csv
import time
app = Flask(__name__)

app.secret_key = "nuishhe834j4r5"
app.config['SESSION_COOKIE_NAME'] = 'Sak Cookies'
TOKEN_INFO = "token_info"
@app.route('/')
def login():
    spotify_oauthorization = helper.create_spotify_oauth()
    authorize_url = spotify_oauthorization.get_authorize_url()
    return redirect(authorize_url)

@app.route('/redirect')
def redirectpage():
    spotify_oauthorization = helper.create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = spotify_oauthorization.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return render_template("index.html")



@app.route('/get_user_track')
def getTracks():
    try:
        token_info = helper.get_user_token(TOKEN_INFO)
    except:
        print("user not logged in")
        redirect(url_for("login", _external = False))
    sp = spotipy.Spotify(auth=token_info['access_token'])
    
    songs = []
    artists = []
    artist_name = []
    popularity = []
    Happy,Sad,Calm,Energetic,mood,emotion,Length, Danceability, Acousticness, Energy, Instrumentalness, Liveness, Valence, Loudness, Speechiness, Tempo = ([] for i in range(10))
    Valence_weight = 1
    Energy_weight = 0.6
    Danceability_weight = 0.4
    for offsetamount in range(6):
        saved_tracks = sp.current_user_saved_tracks(limit=50, offset=offsetamount*50)['items']
    
        for i in range(len(saved_tracks)):
            songs.append(saved_tracks[i]['track']['name'])
            artists.append(saved_tracks[i]['track']['artists'][0]['name'])
            
            popularity.append(saved_tracks[i]['track']['popularity'])
        #get audio feature
        feature = []
        
        for i in range(len(saved_tracks)):
            # Make the API request
            test_track = saved_tracks[i]['track']['id']
            #print(test_track)
            test_feature = None
            delay = 1
            time.sleep(delay)
            while test_feature is None:
                try:
                    test_feature = sp.audio_features(test_track)
                except spotipy.exceptions.SpotifyException as e:
                    
                    if e.http_status == 429:
                        
                        # Rate limit exceeded, implement exponential backoff
                        delay = 2 * delay  # Increase delay exponentially
                        print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                        
                        time.sleep(delay)
                    else:
                        # Other error occurred, handle it accordingly
                        raise e

            for feature in range(len(test_feature)):
                Length.append((int(test_feature[feature]['duration_ms']) / 1000)/60)
                Danceability.append(test_feature[feature]['danceability'])
                Acousticness.append(test_feature[feature]['acousticness'])
                Energy.append(test_feature[feature]['energy'])
                Instrumentalness.append(test_feature[feature]['instrumentalness'])
                Liveness.append(test_feature[feature]['liveness'])
                Valence.append(test_feature[feature]['valence'])
                Loudness.append(test_feature[feature]['loudness'])
                Speechiness.append(test_feature[feature]['speechiness'])
                Tempo.append(test_feature[feature]['tempo'])
                
                valence_value = test_feature[feature]['valence']
                energy_value = test_feature[feature]['energy']
                danceability_value = test_feature[feature]['danceability']
                
                happy_value = helper.get_happy_value(valence_value,energy_value)
                sad_value = helper.get_sad_value(valence_value,energy_value)
                calm_value = helper.get_calm_value(danceability_value, energetic_value)
                energetic_value = helper.get_energetic_value(danceability_value, energetic_value)
                
                Happy.append(happy_value)
                Sad.append(sad_value)
                Calm.append(calm_value)
                Energetic.append(energetic_value)
                if happy_value > sad_value:
                    mood.append("Happy")
                else:
                    mood.append("Sad")
                if energetic_value > calm_value:
                    emotion.append("Energetic")
                else:
                        emotion.append("Calm")
                
    happycount, sadcount,calmcount,energetic_count = 0,0,0,0
    for i in mood:
        if i == "Happy":
            happycount += 1
        else:
            sadcount += 1
    for i in emotion:
        if i == "Calm":
            calmcount +=1
        else:
            energetic_count +=1
            
    if happycount > sadcount:
        mood_result = "Happy"
        mood_percentage = (happycount * 100)/(happycount + sadcount)
    else:
        mood_result = "Sad"
        mood_percentage = (sadcount * 100) / (happycount + sadcount)
        
    if calmcount > energetic_count:
        emotion_result = "Calm"
        emotion_percentage = (calmcount * 100)/(energetic_count + calmcount)
    else:
        emotion_result = "Energetic"
        emotion_percentage = (energetic_count * 100) / (energetic_count + calmcount)    
    data = {
        'Song Name': songs,
        'Artist': artists,
        'Length': Length,
        'Popularity': popularity,
        'Danceability':Danceability,
        'Acousticness':Acousticness,
        'Energy':Energy,
        'Instrumentalness':Instrumentalness,
        'Liveness':Liveness,
        'Valence':Valence,
        'Loudness':Loudness,
        'Speechiness':Speechiness,
        'Tempo':Tempo
    }
    
    # Create a DataFrame from the data dictionary
    df = pd.DataFrame(data)
    
    # Export DataFrame to a CSV file
    df.to_excel('tracks.xlsx', index=False)
    return render_template("Get_user_track.html", spotify_link = link, mood_result = mood_result, mood_percentage = mood_percentage, emotion_result = emotion_result, emotion_percentage = emotion_percentage, Name = songs, artist = artists, mood = mood, emotion = emotion, happy = Happy, sad = Sad, energetic = Energetic, calm = Calm,
                           length = Length, danceability = Danceability, acousticness = Acousticness, energy = Energy, instrumentalness = Instrumentalness,
                           liveness = Liveness, valence = Valence, loudness = Loudness, speechiness = Speechiness,tempo = Tempo)

@app.route('/getplaylist', methods = ["GET", "POST"])
def getplaylist():
    try:
        token_info = helper.get_user_token(TOKEN_INFO)
    except:
        print("user not logged in")
        redirect(url_for("login", _external = False))
        
    sp = spotipy.Spotify(auth=token_info['access_token'])
    link = request.form.get("link")
        # Split the URL by '/'
    url_parts = link.split('/')

    # Get the playlist ID from the URL parts
    playlist_id = url_parts[-1].split('?')[0]
    #print(playlist_id)
    
    token_info = helper.get_user_token(TOKEN_INFO)
    sp = spotipy.Spotify(auth=token_info['access_token'])
    
    playlist = sp.playlist(playlist_id)
    #print(playlist['name'])
    
    playlist = playlist['tracks']
    tracks = helper.get_playlist_track_name(playlist)
    artist = helper.get_playlist_track_artist(playlist)
    id = helper.get_track_id(playlist)
    feature = sp.audio_features(id[0])
  
    songs,artists,Length, Danceability, Acousticness, Energy, Instrumentalness, Liveness, Valence, Loudness, Speechiness, Tempo, Happy, Sad, Energetic, Calm, mood, emotion= ([] for i in range(18))

    for track in playlist['items']:
        # Extract track information
        track_info = track['track']
        songs.append(track_info['name'])
        artists.append(track_info['artists'][0]['name'])
        #print(track_info['name'])
        test_feature = sp.audio_features(track_info['id'])
        Length.append((int(test_feature[0]['duration_ms']) / 1000) / 60)
        Danceability.append(test_feature[0]['danceability'])
        Acousticness.append(test_feature[0]['acousticness'])
        Energy.append(test_feature[0]['energy'])
        Instrumentalness.append(test_feature[0]['instrumentalness'])
        Liveness.append(test_feature[0]['liveness'])
        Valence.append(test_feature[0]['valence'])
        Loudness.append(test_feature[0]['loudness'])
        Speechiness.append(test_feature[0]['speechiness'])
        Tempo.append(test_feature[0]['tempo'])
        
        valence_value = test_feature[0]['valence']
        energy_value = test_feature[0]['energy']
        danceability_value = test_feature[0]['danceability']
        instrumentalness_value = test_feature[0]['instrumentalness']
        
        happy_value = helper.get_happy_value(valence_value, energy_value, danceability_value)
        sad_value = helper.get_sad_value(valence_value, energy_value, danceability_value)
        calm_value = helper.get_calm_value(danceability_value, energy_value, valence_value, instrumentalness_value)
        energetic_value = helper.get_energetic_value(danceability_value, energy_value, valence_value, instrumentalness_value)
            
            
        Happy.append(happy_value)
        Sad.append(sad_value)
        Calm.append(calm_value)
        Energetic.append(energetic_value)
        
        if happy_value > sad_value:
            mood.append("Happy")
        else:
            mood.append("Sad")
        if energetic_value > calm_value:
            emotion.append("Energetic")
        else:
                emotion.append("Calm")
    
    while playlist['next']:
        playlist = sp.next(playlist['tracks'])    
        tracks = helper.get_track_name(playlist)
        artist = helper.get_track_artist(playlist)
        id = helper.get_track_id(playlist)

        for i in range(len(tracks)):
            songs.append(tracks[i])
            artists.append(artist[i])
            test_feature = sp.audio_features(id[i])
            Length.append((int(test_feature[0]['duration_ms']) / 1000) / 60)
            Danceability.append(test_feature[0]['danceability'])
            Acousticness.append(test_feature[0]['acousticness'])
            Energy.append(test_feature[0]['energy'])
            Instrumentalness.append(test_feature[0]['instrumentalness'])
            Liveness.append(test_feature[0]['liveness'])
            Valence.append(test_feature[0]['valence'])
            Loudness.append(test_feature[0]['loudness'])
            Speechiness.append(test_feature[0]['speechiness'])
            Tempo.append(test_feature[0]['tempo'])
            
            valence_value = test_feature[0]['valence']
            energy_value = test_feature[0]['energy']
            danceability_value = test_feature[0]['danceability']
            instrumentalness_value = test_feature[0]['instrumentalness']
            happy_value = helper.get_happy_value(valence_value, energy_value, danceability_value)
            sad_value = helper.get_sad_value(valence_value, energy_value, danceability_value)
            calm_value = helper.get_calm_value(danceability_value, energy_value, valence_value, instrumentalness_value)
            energetic_value = helper.get_energetic_value(danceability_value, energy_value, valence_value, instrumentalness_value)
            
            
            
            Happy.append(happy_value)
            Sad.append(sad_value)
            Calm.append(calm_value)
            Energetic.append(energetic_value)
            if happy_value > sad_value:
                mood.append("Happy")
                
            else:
                mood.append("Sad")
                
                
            if energetic_value > calm_value:
                emotion.append("Energetic")
             
            else:
                emotion.append("Calm")
            
    happycount, sadcount,calmcount,energetic_count = 0,0,0,0
    for i in mood:
        if i == "Happy":
            happycount += 1
        else:
            sadcount += 1
    for i in emotion:
        if i == "Calm":
            calmcount +=1
        else:
            energetic_count +=1
            
    if happycount > sadcount:
        mood_result = "Happy"
        mood_percentage = (happycount * 100)/(happycount + sadcount)
    else:
        mood_result = "Sad"
        mood_percentage = (sadcount * 100) / (happycount + sadcount)
        
    if calmcount > energetic_count:
        emotion_result = "Calm"
        emotion_percentage = (calmcount * 100)/(energetic_count + calmcount)
    else:
        emotion_result = "Energetic"
        emotion_percentage = (energetic_count * 100) / (energetic_count + calmcount)
    data = {
        'Song Name': songs,
        'Artist': artists,
        'Length': Length,
        
        'Danceability':Danceability,
        'Acousticness':Acousticness,
        'Energy':Energy,
        'Instrumentalness':Instrumentalness,
        'Liveness':Liveness,
        'Valence':Valence,
        'Loudness':Loudness,
        'Speechiness':Speechiness,
        'Tempo':Tempo,
        'Happy' :Happy,
        'Sad' :Sad,
        'Energetic' :Energetic,
        'Calm' :Calm,
        'Mood' : mood,
        'Emotion' :emotion
    }
    # #Create a DataFrame from the data dictionary
    # df = pd.DataFrame(data)
    

    # #Export DataFrame to a CSV file
    # df.to_excel('sample.xlsx', index=False)
    
    return render_template("dashboardjs.html", spotify_link = link, mood_result = mood_result, mood_percentage = mood_percentage, emotion_result = emotion_result, emotion_percentage = emotion_percentage, Name = songs, artist = artists, mood = mood, emotion = emotion, happy = Happy, sad = Sad, energetic = Energetic, calm = Calm,
                           length = Length, danceability = Danceability, acousticness = Acousticness, energy = Energy, instrumentalness = Instrumentalness,
                           liveness = Liveness, valence = Valence, loudness = Loudness, speechiness = Speechiness,tempo = Tempo)

@app.route('/gettrack',methods = ["GET", "POST"])
def gettrack():
    try:
        token_info = helper.get_user_token(TOKEN_INFO)
    except:
        print("user not logged in")
        redirect(url_for("login", _external = False))
        
    sp = spotipy.Spotify(auth=token_info['access_token'])
    link = request.form.get("track_link")
        # Split the URL by '/'
    url_parts = link.split('/')

    # Get the track ID from the URL parts
    track_id = url_parts[-1].split('?')[0]
    #print(playlist_id)
    
    token_info = helper.get_user_token(TOKEN_INFO)
    sp = spotipy.Spotify(auth=token_info['access_token'])
    
    track = sp.track(track_id)
    track_name = track['name']
    track_artist =track['artists'][0]['name']
    
    track_feature = sp.audio_features(track_id)
    
    Valence_weight = 1
    Energy_weight = 0.6
    Danceability_weight = 0.4
    
    
    Length = ((int(track_feature[0]['duration_ms']) / 1000) / 60)
    Danceability = (track_feature[0]['danceability'])
    Acousticness = (track_feature[0]['acousticness'])
    Energy = (track_feature[0]['energy'])
    Instrumentalness = (track_feature[0]['instrumentalness'])
    Liveness = (track_feature[0]['liveness'])
    Valence = (track_feature[0]['valence'])
    Loudness = (track_feature[0]['loudness'])
    Speechiness = (track_feature[0]['speechiness'])
    Tempo = (track_feature[0]['tempo'])
    
    happy_value = helper.get_happy_value(Valence, Energy, Danceability)
    sad_value = helper.get_sad_value(Valence,Energy, Danceability)
    calm_value = helper.get_calm_value(Danceability, Energy, Valence, Instrumentalness)
    energetic_value = helper.get_energetic_value(Danceability, Energy, Valence, Instrumentalness)
    
    mood_value_normalizer = 1/ (happy_value + sad_value)
    emotion_value_normalizer = 1 / (calm_value + energetic_value)
    
    happy_value = mood_value_normalizer * happy_value
    sad_value = mood_value_normalizer * sad_value
    calm_value = emotion_value_normalizer * calm_value
    energetic_value = emotion_value_normalizer * energetic_value
    
    if happy_value > sad_value:
        mood_result = "Happy"
        mood_percentage = 100 * happy_value
    else:
        mood_result = "Sad"
        mood_percentage = 100 * sad_value
    
    if calm_value > energetic_value:
        emotion_result = "Calm"
        emotion_percentage =  100 * calm_value
        
    else:
        emotion_result = "Energetic"
        emotion_percentage = 100 * energetic_value
    
    return render_template("trackdashboard.html", mood_result = mood_result, mood_percentage = mood_percentage, emotion_result = emotion_result, emotion_percentage = emotion_percentage, Name = track_name, artist = track_artist, mood = mood_result, emotion = emotion_result, happy = happy_value, sad = sad_value, energetic = energetic_value, calm = calm_value,
                           length = Length, danceability = Danceability, acousticness = Acousticness, energy = Energy, instrumentalness = Instrumentalness,
                           liveness = Liveness, valence = Valence, loudness = Loudness, speechiness = Speechiness,tempo = Tempo)
    
@app.route('/reccomendation')
def reccomendation():
    try:
        token_info = helper.get_user_token(TOKEN_INFO)
    except:
        print("user not logged in")
        redirect(url_for("login", _external = False))
        
    sp = spotipy.Spotify(auth=token_info['access_token'])
    link = request.form.get("link")
        # Split the URL by '/'
    url_parts = link.split('/')

    # Get the playlist ID from the URL parts
    playlist_id = url_parts[-1].split('?')[0]
    #print(playlist_id)
    
    token_info = helper.get_user_token(TOKEN_INFO)
    sp = spotipy.Spotify(auth=token_info['access_token'])
    
    


client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")