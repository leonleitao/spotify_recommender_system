import requests
import json

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from . import config


class User:
    """
    Gets the user's saved tracks and builds recommendations.
    """
    def __init__(self, token):
        self.token = token
        self.features = pd.read_csv(
            config.DATASET_DIR / config.DATASET_PREPROCESSED_NAME
            )
        self.saved_tracks = None
        self.recommended_tracks = None
        self.user_id = None

    def _user_saved_tracks(self):
        """Gets the user's saved tracks (limit 30)"""
        # Get request to pull user saved tracks
        res = requests.get(
            config.USER_TRACKS_URL,
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )
        res = res.json()
        return res

    def _get_song_details(self, res):
        """Extracts and returns the artist names and song names from the json response"""
        artist_names = []
        song_names = []
        for idx, item in enumerate(res['items']):
            track = item['track']
            artist_names.append(track['artists'][0]['name'])
            song_names.append(track['name'])
        return song_names, artist_names

    def _find_saved_indices(self,song_names,artist_names):
        """Returns the indices of the saved tracks in the song features dataset"""
        indices = []
        # Matches songs based on the name and artist name
        for name, artist in zip(song_names, artist_names):
            song_indices = list(self.features[self.features.name.str.contains(name) & self.features.artists.str.contains(artist)].index)
            indices+=song_indices
        return indices

    def get_saved_tracks(self):
        """Returns a dataframe of the user's saved tracks"""
        res = self._user_saved_tracks()
        song_names, artist_names = self._get_song_details(res)
        saved_indices = self._find_saved_indices(song_names,artist_names)
        saved_tracks = self.features.loc[saved_indices]
        saved_tracks = saved_tracks.drop_duplicates(subset=['name'])
        # Add saved tracks and indices as attributes
        self.saved_tracks = saved_tracks
        self.saved_indices = saved_indices
        return saved_tracks

    def _calculate_cosine_similarities(self):
        """Returns cosine similarity scores between saved tracks and other tracks in the data"""
        # Drop irrelevant columns
        cols_to_drop = ['artists', 'id', 'name']
        X = self.features.drop(cols_to_drop, axis=1)
        Y = self.saved_tracks.drop(cols_to_drop, axis=1)
        # Calculate cosine similarity scores
        scores = cosine_similarity(X, Y)
        return scores

    def _get_recommended_indices(self, scores):
        """Returns indices of the recommended tracks in the song features dataset"""
        recommended_indices = []
        # Finds the TOP_N songs for each song in the users saved tracks
        for i in range(scores.shape[1]):
            top_indices = np.argpartition(scores[:, i], -config.TOP_N-1)[-config.TOP_N-1:]
            for index in top_indices:
                if index not in self.saved_indices:
                    recommended_indices.append(index)
        return recommended_indices

    def get_recommended_tracks(self):
        """Returns a dataframe of recommended tracks"""
        if not self.saved_tracks:
            self.get_saved_tracks()
        scores = self._calculate_cosine_similarities()
        recommended_indices = self._get_recommended_indices(scores)
        recommended_tracks = self.features.loc[recommended_indices]
        recommended_tracks = recommended_tracks.drop_duplicates(subset=['name'])
        self.recommended_tracks = recommended_tracks
        return recommended_tracks


# UTILITY FUNCTIONS
def get_track_info(track_ids, token):
    """
    Gets the name, artist and album for a list of track ids
    :param track_ids: list of track ids
    :param token: user access token
    :return: dictionary of track information
    """
    track_info = []
    url_args = 'ids=' + ','.join(track_ids)
    query = f'{config.TRACKS_URL}?{url_args}'
    res = requests.get(
                query,
                headers={
                    "Authorization": f"Bearer {token}"
                }
            )
    res = res.json()['tracks']

    for r in res:
        track = dict()
        track['name'] = r['name']
        track['album'] = r['album'].get('name')
        track['artists'] = ", ".join([artist.get('name') for artist in r['artists']])
        track['spotify_url'] = r['external_urls'].get('spotify')
        track_info.append(track)

    return track_info


def get_user_id(token):
    """
    Gets the user's id
    :param token: user access token
    :return: user id
    """
    res = requests.get(
        config.USER_URL,
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    res = res.json()
    user_id = res['id']
    return user_id


def create_empty_playlist(name, user_id, token):
    """
    Creates and empty playlist and returns the playlist id and url
    :param name: name of the playlist
    :param user_id: user id
    :param token: user access token
    :return: new playlist id
    :return: new playlist url
    """
    URL = config.API_URL + f"/users/{user_id}/playlists"
    body = json.dumps({
        "name": name,
        "description": "Custom song recommendations",
        "public": True
    })
    res = requests.post(
        URL,
        data=body,
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    res = res.json()
    return res["id"], res["external_urls"].get('spotify')


def add_playlist_tracks(playlist_id, track_ids, token):
    """
    Adds a list of tracks to a playlist
    :param playlist_id: playlist id
    :param track_ids: list of track ids to be added.
    :param token: user access token
    :return: response from post request
    """
    uris = [f'spotify:track:{track_id}' for track_id in track_ids]
    request_data = json.dumps(uris)
    URL = config.API_URL + f"/playlists/{playlist_id}/tracks"

    res = requests.post(
        URL,
        data=request_data,
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    return res
