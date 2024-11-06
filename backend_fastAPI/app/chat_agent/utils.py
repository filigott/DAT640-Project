from enum import Enum, auto
import random
import re
from typing import Dict

# Endpoints for API services
RASA_URL = "http://localhost:5005/model/parse"

RANDOM_QUESTION_CHANCE = 0.5
MAX_NUM_SONGS = 5

class IntentType(Enum):
    SONG = "song"
    ARTIST = "artist"
    ALBUM = "album"

class Intents(Enum):
    ask_song_release_date = 0
    ask_songs_of_artist = auto()
    ask_artist_of_song = auto()
    ask_album_release_date = auto()
    ask_album_of_song = auto()
    ask_albums_of_artist = auto()
    # NEW
    add_song_to_playlist = auto()
    remove_song_from_playlist = auto()
    list_songs_in_playlist = auto()
    empty_playlist = auto()


class Commands(Enum):
    hello = "/hello"
    exit = "/exit"
    parrot = "/parrot"
    seed = "/seed"
    add = "/add"
    remove = "/remove"
    view = "/view"
    clear = "/clear"

def generate_example_questions(song_description):
    """Generates example questions based on song data."""
    questions = {
        Intents.ask_song_release_date: f"When was the song '{song_description.get('title')}' released?",
        Intents.ask_songs_of_artist: f"What songs does '{song_description.get('artist')}' have?",
        Intents.ask_album_of_song: f"Which album is the song '{song_description.get('title')}' from?",
    }
    return random.choice(list(questions.values()))


def parse_add_song_input(input_text):
    # First, ensure the command starts with "/add"
    if not input_text.startswith("/add "):
        return None, None

    # Remove the "/add " prefix
    command_text = input_text[5:].strip()

    # Try to match both patterns
    # Pattern 1: "[artist]: [title]"
    match1 = re.match(r'^(.*):\s*(.*)$', command_text)
    # Pattern 2: "[title] by [artist]"
    match2 = re.match(r'^(.*)\s+by\s+(.*)$', command_text, re.IGNORECASE)

    if match1:
        artist, title = match1.groups()
    elif match2:
        title, artist = match2.groups()
    else:
        return None, None  # If no patterns matched

    # Return the extracted artist and title without any additional formatting
    return artist.strip(), title.strip()
