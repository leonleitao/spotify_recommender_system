import requests
import random
import json

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from . import config


class User:
    def __init__(self, token):
        self.token = token
        self.features = pd.read_csv(
            config.DATASET_DIR / config.DATASET_PREPROCESSED_NAME
            )
        self.saved_tracks = None
        self.recommended_tracks = None
        self.user_id = None

    def _user_saved_tracks(self):
        res = requests.get(
            config.USER_TRACKS_URL,
            headers={
                "Authorization": f"Bearer {token}"
            }
        )
        res = res.json()
        return res

    def _get_song_details(self, res):
        artist_names = []
        song_names = []
        for idx, item in enumerate(res['items']):
            track = item['track']
            artist_names.append(track['artists'][0]['name'])
            song_names.append(track['name'])
        return song_names, artist_names

    def _find_saved_indices(self):
        indices = []
        res = self._user_saved_tracks()
        song_names, artist_names = self._get_song_details(res)
        for name, artist in zip(song_names, artist_names):
            song_indices = list(self.features[self.features.name.str.contains(name) & self.features.artists.str.contains(artist)].index)
            indices + = song_indices
        return indices

    def get_saved_tracks(self):
        # Create dataframe of saved/saved tracks
        saved_indices = self._find_saved_indices()
        saved_tracks = self.features.loc[saved_indices]
        saved_tracks = saved_tracks.drop_duplicates(subset=['name'])
        self.saved_tracks = saved_tracks
        self.saved_indices = saved_indices
        return saved_tracks

    def _calculate_cosine_similarities(self):
        # Drop irrelevant columns
        cols_to_drop = ['artists', 'id', 'name']
        X = self.features.drop(cols_to_drop, axis=1)
        Y = self.saved_tracks.drop(cols_to_drop, axis=1)
        # Calculate cosine similarity scores
        scores = cosine_similarity(X, Y)
        return scores

    def _get_recommended_indices(self):
        if not self.saved_tracks:
            self.get_saved_tracks()
        # Get list of recomended song indices
        scores = self._calculate_cosine_similarities()
        recommended_indices = []
        for i in range(scores.shape[1]):
            top_indices = np.argpartition(scores[:, i], -config.TOP_N-1)[-config.TOP_N-1:]
            for index in top_indices:
                if index not in self.saved_indices:
                    recommended_indices.append(index)
        return recommended_indices

    def get_recommended_tracks(self):
        # Get dataframe of recommended tracks
        recommended_indices = self._get_recommended_indices()
        recommended_tracks = self.features.loc[recommended_indices]
        recommended_tracks = recommended_tracks.drop_duplicates(subset=['name'])
        self.recommended_tracks = recommended_tracks
        return recommended_tracks


# UTILITY FUNCTIONS
def get_track_info(track_ids, token):
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
