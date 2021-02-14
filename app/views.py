from urllib.parse import quote
import random
import os
import requests
import json

from flask import Blueprint
from flask import Flask, render_template, url_for, redirect, request, session, jsonify, flash, Blueprint

from .recommendations import User, create_empty_playlist, add_playlist_tracks, get_user_id, get_track_info
from . import config


view = Blueprint("views", __name__,template_folder='templates',static_folder='static',url_prefix="/")

@view.route("/")
@view.route("/home")
def home():
    return render_template('home.html')

@view.route("/authorization")
def authorization():
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in config.AUTH_QUERY_PARAMETERS.items()])
    auth_url = f"{config.AUTH_URL}/?{url_args}"
    return redirect(auth_url)

@view.route("/callback/q")
def callback():
    # Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": config.REDIRECT_URI,
        'client_id': config.CLIENT_ID,
        'client_secret': config.CLIENT_SECRET,
    }
    post_request = requests.post(config.TOKEN_URL, data=code_payload)
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    
    user = User(access_token)
    recommended_tracks = user.get_recommended_tracks()
    track_ids = list(recommended_tracks.id)
    
    session['access_token'] = access_token
    session['recommended_tracks'] = track_ids

    user_id = get_user_id(session['access_token'])
    session['user_id'] = user_id

    return redirect(url_for('views.recommendations'))

@view.route("/recommendations")
def recommendations():
    track_ids = random.sample(session['recommended_tracks'], config.PLAYLIST_NUM_TRACKS)
    session['track_ids'] = track_ids
    track_info = get_track_info(track_ids, session['access_token'])
    return render_template('recommendations.html', title='Recommendations', tracks=track_info)

@view.route("/add_playlist", methods=['POST'])
def add_playlist():
    name = request.form.get('name')
    playlist_id, url = create_empty_playlist(name, session['user_id'], session['access_token'])
    res = add_playlist_tracks(playlist_id, session['track_ids'], session['access_token'])
    message = f'Successfully added playlist {name} to your Spotify account.'        
    return jsonify({'message': message, 'url':url})