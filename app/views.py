from urllib.parse import quote
import random
import requests
import json

from flask import render_template, url_for, redirect, request, session, jsonify, Blueprint

from .recommendations import User, create_empty_playlist, add_playlist_tracks, get_user_id, get_track_info
from . import config


view = Blueprint("views", __name__, template_folder='templates', static_folder='static', url_prefix="/")

@view.route("/")
@view.route("/home")
def home():
    """
    Displays home page
    :return: None
    """
    return render_template('home.html')


@view.route("/authorization")
def authorization():
    """
    Redirects to Spotify authorization url
    :return: None
    """
    # Ask for user permission
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in config.AUTH_QUERY_PARAMETERS.items()])
    auth_url = f"{config.AUTH_URL}/?{url_args}"
    return redirect(auth_url)


@view.route("/callback/q")
def callback():
    """
    Makes requests for an access token and uses it to build recommendations for the user
    :return: None
    """
    # Request refresh and access tokens
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
    # Create a user object using the token
    user = User(access_token)
    # Build recommendations using saved tracks
    recommended_tracks = user.get_recommended_tracks()
    global recommended_ids
    recommended_ids = list(recommended_tracks.id)
    user_id = get_user_id(access_token)
    # Add token, tracks and user id to sessions object
    session['access_token'] = access_token
    session['user_id'] = user_id
    return redirect(url_for('views.recommendations', _external=True, _scheme="https"))


@view.route("/recommendations")
def recommendations():
    """
    Displays a playlist of recommendations to the user
    :return: None
    """
    # Generete a random sample from the recommended tracks to display as a playlist
    global recommended_ids
    track_ids = random.sample(recommended_ids, config.PLAYLIST_NUM_TRACKS)
    session['track_ids'] = track_ids
    track_info = get_track_info(track_ids, session['access_token'])
    return render_template('recommendations.html', title='Recommendations', tracks=track_info)


@view.route("/add_playlist", methods=['POST'])
def add_playlist():
    """
    Adds the playlist to the user's Spotify account
    :return: Success/Error message
    """
    # Get the user's playlist name
    name = request.form.get('name')
    playlist_id, url = create_empty_playlist(name, session['user_id'], session['access_token'])
    res = add_playlist_tracks(playlist_id, session['track_ids'], session['access_token'])
    message = f'Added playlist {name} to your Spotify account.'
    return jsonify({'message': message, 'url': url})

