import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATASET_DIR = ROOT / "data"
DATASET_RAW = 'data.csv'
DATASET_PREPROCESSED_NAME = 'data_preprocessed.csv'

# PREPROCESSING
# Since we use cosine similarity to recommend tracks all the features should have the same scale (0-1)
# List of numerical columns to scale using MinMaxscaler from sklearn
COLUMNS_TO_SCALE = [
    'acousticness', 
    'danceability', 
    'duration_ms', 
    'energy',
    'instrumentalness', 
    'key', 
    'liveness', 
    'loudness',
    'popularity', 
    'speechiness', 
    'tempo',
    'valence', 
    'year'
]

# List of columns that are irrelevant and need to be dropped
COLUMNS_TO_DROP = [
    'release_date'
]

# Column that needs to be converted from a string to a list
STRING_COLUMN_TO_LIST = 'artists'
