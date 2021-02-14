import pathlib
import os

# ROOT DIRECTORY
ROOT = pathlib.Path(__file__).resolve().parent.parent

# DATA DIRECTORIES AND FILENAMES
DATASET_DIR = ROOT / "data"
DATASET_RAW_NAME = 'data.csv'
DATASET_PREPROCESSED_NAME = 'data_preprocessed.csv'

# CLIENT KEYS
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

# SPOTIFY URLS
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_URL = "https://api.spotify.com/v1"
USER_TRACKS_URL = "https://api.spotify.com/v1/me/tracks?offset=0&limit=30"
USER_URL = "https://api.spotify.com/v1/me"
TRACKS_URL = "https://api.spotify.com/v1/tracks"

# SERVER SIDE PARAMETERS
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 5000
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "user-library-read playlist-modify-public playlist-modify-private"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

AUTH_QUERY_PARAMETERS = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}

# RECOMMENDER SYSTEM PARAMETERS
TOP_N = 15
PLAYLIST_NUM_TRACKS = 10

# APP CONFIGS
class Config:
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    SERVER_PORT = 5000

class ProductionConfig(Config):
    DEBUG = False
    SERVER_ADDRESS: os.environ.get('SERVER_ADDRESS', '0.0.0.0')
    SERVER_PORT: os.environ.get('SERVER_PORT', '5000')

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class TestingConfig(Config):
    TESTING = True