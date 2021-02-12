import requests
import random
import pandas as pd
import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity

TRACK_URI = "https://api.spotify.com/v1/me/tracks?offset=0&limit=30"
USER_URI = "https://api.spotify.com/v1/me"
NUM_TRACKS = 5

class User:
    def __init__(self,token):
        self.token = token
        self.features = pd.read_csv('data/data_preprocessed.csv')
        self.saved_tracks = None
        self.recommended_tracks = None
        self.user_id = None
    
    def _user_saved_tracks(self):
        res = requests.get(
            TRACK_URI,
            headers={
                "Authorization": "Bearer {}".format(self.token)
            }
        )
        res=res.json()
        return res
    
    def _get_song_details(self,res):
        artist_names=[]
        song_names=[]
        for idx, item in enumerate(res['items']):
            track = item['track']
            artist_names.append(track['artists'][0]['name'])
            song_names.append(track['name'])
        return song_names,artist_names
    
    def _find_saved_indices(self):
        indices=[]
        res=self._user_saved_tracks()
        song_names,artist_names=self._get_song_details(res)
        for name,artist in zip(song_names,artist_names):
            song_indices=list(self.features[self.features.name.str.contains(name) & self.features.artists.str.contains                                  (artist)].index)
            indices+=song_indices
        return indices
    
    def get_saved_tracks(self):
        # Create dataframe of saved/saved tracks
        saved_indices=self._find_saved_indices()
        saved_tracks=self.features.loc[saved_indices]
        saved_tracks=saved_tracks.drop_duplicates(subset=['name'])
        self.saved_tracks=saved_tracks
        self.saved_indices=saved_indices
        return saved_tracks
    
    def _calculate_cosine_similarities(self):
        # Drop irrelevant columns
        cols_to_drop=['artists','id','name']
        X=self.features.drop(cols_to_drop,axis=1)
        Y=self.saved_tracks.drop(cols_to_drop,axis=1)
        # Calculate cosine similarity scores
        scores=cosine_similarity(X,Y)
        return scores
    
    def _get_recommended_indices(self):
        if not self.saved_tracks:
            self.get_saved_tracks()
        # Get list of recomended song indices
        scores=self._calculate_cosine_similarities()
        recommended_indices=[]
        for i in range (scores.shape[1]):
            top_indices=np.argpartition(scores[:,i],-NUM_TRACKS-1)[-NUM_TRACKS-1:]
            for index in top_indices:
                if index not in self.saved_indices:
                    recommended_indices.append(index)
        return recommended_indices

    def get_recommended_tracks(self):
        # Get dataframe of recommended tracks
        recommended_indices=self._get_recommended_indices()
        recommended_tracks=self.features.loc[recommended_indices]
        recommended_tracks=recommended_tracks.drop_duplicates(subset=['name'])
        self.recommended_tracks=recommended_tracks
        return recommended_tracks
    
    def generate_playlist(self,n_tracks=10):
        if self.recommended_tracks is not None:
            track_ids=list(self.recommended_tracks.id)
            track_ids=random.sample(track_ids,n_tracks)
            return track_ids
        return

    
    def add_playlist(self,name,track_ids):
        playlist_id=self._create_empty_playlist(name)
        uris=[f'spotify:track:{track_id}' for track_id in track_ids]
        request_data = json.dumps(uris)
        URI = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

        res = requests.post(
            URI,
            data=request_data,
            headers={
                "Authorization": "Bearer {}".format(self.token)
            }
        )
        
        return

    def _create_empty_playlist(self,name="Recommendations_playlist"):
        if not self.user_id:
            self._get_user_id()
        URI=f"https://api.spotify.com/v1/users/{self.user_id}/playlists"
        
        body = json.dumps({
            "name": name,
            "description": "Custom song recommendations",
            "public": True
        })

        res = requests.post(
            URI,
            data=body,
            headers={
                "Authorization": "Bearer {}".format(self.token)
            }
        )
        res=res.json()
        print(f'Playlist created at ',res['external_urls'].get('spotify'))
        # playlist id
        return res["id"]

    def _get_user_id(self):
        res = requests.get(
            USER_URI,
            headers={
                "Authorization": "Bearer {}".format(self.token)
            }
        )
        res=res.json()
        self.user_id=res['id']
        return

