from flask import Blueprint
from flask import Flask, render_template, url_for, redirect, request, session, jsonify, flash, Blueprint

from urllib.parse import quote
import random
import os
import requests
import json

from .recommendations import User

view = Blueprint("views", __name__,template_folder='templates',static_folder='static',url_prefix="/")

# CLIENT KEYS
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

# SPOTIFY URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1"

# SERVER SIDE PARAMETERS
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 5000
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "user-library-read playlist-modify-public playlist-modify-private"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}

@view.route("/")
@view.route("/home")
def home():
    return render_template('home.html')

@view.route("/authorization")
def authorization():
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)

@view.route("/callback/q")
def callback():
    # Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    
    user=User(access_token)
    _ = user.get_recommended_tracks()
    track_ids=list(user.recommended_tracks.id)
    
    session['access_token'] = access_token
    session['recommended_tracks'] = track_ids

    user_id = get_user_id()
    session['user_id'] = user_id

    return redirect(url_for('views.recommendations'))

@view.route("/recommendations")
def recommendations():
    track_ids=random.sample(session['recommended_tracks'],10)
    session['track_ids']=track_ids
    track_info=get_track_info(track_ids)
    return render_template('recommendations.html',title='Recommendations',tracks=track_info)

@view.route("/add_playlist", methods=['POST'])
def add_playlist():
    
    name=request.form.get('name')
    playlist_id, url = create_empty_playlist(name)
    uris=[f'spotify:track:{track_id}' for track_id in session['track_ids']]
    request_data = json.dumps(uris)
    URI = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    res = requests.post(
        URI,
        data=request_data,
        headers={
            "Authorization": "Bearer {}".format(session['access_token'])
        }
    )
    # url='https://www.google.com'
    message=f'Successfully added playlist {name} to your Spotify account.'        
    return jsonify({'message': message,'url':url})

def get_track_info(track_ids):
    track_info=[]
    uri='https://api.spotify.com/v1/tracks'
    url_args='ids=' + ','.join(track_ids)
    query=f'{uri}?{url_args}'
    res = requests.get(
                query,
                headers={
                    "Authorization": "Bearer {}".format(session['access_token'])
                }
            )
    res=res.json()['tracks']
    
    for r in res:
        track=dict()
        track['name'] = r['name']
        track['album'] = r['album'].get('name')
        track['artists'] = ", ".join([artist.get('name') for artist in r['artists']])
        track['spotify_url'] = r['external_urls'].get('spotify')
        track_info.append(track)

    return track_info

def get_user_id():
    USER_URI = "https://api.spotify.com/v1/me"
    res = requests.get(
        USER_URI,
        headers={
            "Authorization": "Bearer {}".format(session['access_token'])
        }
    )
    res=res.json()
    user_id=res['id']
    return user_id

def create_empty_playlist(name):
        
        URI=f'https://api.spotify.com/v1/users/{session["user_id"]}/playlists'
        
        body = json.dumps({
            "name": name,
            "description": "Custom song recommendations",
            "public": True
        })

        res = requests.post(
            URI,
            data=body,
            headers={
                "Authorization": "Bearer {}".format(session["access_token"])
            }
        )
        res=res.json()
        return res["id"],res["external_urls"].get('spotify')