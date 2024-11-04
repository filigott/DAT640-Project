from enum import Enum

# Endpoints for API services
# FAST_API_ENDPOINT = "http://localhost:8000"
RASA_URL = "http://localhost:5005/model/parse"

# Intent and entity mappings for API routing
# INTENTS = {
#     "ask_song_release_date": f"{FAST_API_ENDPOINT}/bot/song_release_date",
#     "ask_songs_of_artist": f"{FAST_API_ENDPOINT}/bot/songs_of_artist",
#     "ask_artist_of_song": f"{FAST_API_ENDPOINT}/bot/artist_of_song",
#     "ask_album_release_date": f"{FAST_API_ENDPOINT}/bot/album_release_date",
#     "ask_album_of_song": f"{FAST_API_ENDPOINT}/bot/album_of_song",
#     "ask_albums_of_artist": f"{FAST_API_ENDPOINT}/bot/albums_of_artist"
# }

class IntentType(Enum):
    SONG = "song"
    ARTIST = "artist"
    ALBUM = "album"

class Intents(Enum):
    ask_song_release_date = 1
    ask_songs_of_artist = 2
    ask_artist_of_song = 3
    ask_album_release_date = 4
    ask_album_of_song = 5
    ask_albums_of_artist = 6

class Commands(Enum):
    hello = "/hello"
    exit = "/exit"
    parrot = "/parrot"
    seed = "/seed"
    add = "/add"
    remove = "/remove"
    view = "/view"
    clear = "/clear"
