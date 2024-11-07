from dataclasses import dataclass, field
from enum import Enum, auto
import random
import re
from typing import Dict, List, Optional

from app.schemas import SongSchema

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

    add_song_to_playlist = auto()
    remove_song_from_playlist = auto()
    list_songs_in_playlist = auto()
    empty_playlist = auto()

    remove_from_playlist_position = auto()
    song_release_date_position = auto()
    recommend_songs_based_on_playlist = auto()

    add_all_recommended_songs = auto()
    add_position_recommended_songs = auto()
    add_all_except_recommended_songs = auto()


class Commands(Enum):
    hello = "/hello"
    exit = "/exit"
    parrot = "/parrot"
    seed = "/seed"
    add = "/add"
    remove = "/remove"
    view = "/view"
    clear = "/clear"

class ConversationTopic(Enum):
    add_song = auto()
    recommend_playlist = auto()

class AddSongState(Enum):
    default = 0
    waiting_for_clarification = auto()
    continue_clarification = auto()
    song_added = auto()
    finished = auto()

class RecommendPlaylistState(Enum):
    default = 0
    in_progress = auto()
    finished = auto()

@dataclass
class SongDetails:
    artist: Optional[str] = None
    title: Optional[str] = None
    album: Optional[str] = None
    year: Optional[int] = None

@dataclass
class AddSongContext:
    state: AddSongState = AddSongState.default
    pending_songs: List = field(default_factory=list)

@dataclass
class RecommendPlaylistContext:
    state: RecommendPlaylistState = RecommendPlaylistState.default
    pending_songs: List = field(default_factory=list)

@dataclass
class ConversationContext:
    add_song: AddSongContext = field(default_factory=AddSongContext)
    recommend_playlist: RecommendPlaylistContext = field(default_factory=RecommendPlaylistContext)


def generate_example_questions(song: SongSchema):
    """Generates example questions based on song data."""
    questions = {
        Intents.ask_song_release_date: f"When was the song '{song.title}' released?",
        Intents.ask_songs_of_artist: f"What songs does '{song.artist}' have?",
        Intents.ask_album_of_song: f"Which album is the song '{song.album}' from?",
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
    # Pattern 3: "[title]" (only title, no artist)
    match3 = re.match(r'^(.*)$', command_text)

    artist, title = None, None

    if match1:
        artist, title = match1.groups()
    elif match2:
        title, artist = match2.groups()
    elif match3:
        title = match3.group(1).strip()

    if title is None:
        return None, None  # If no valid title was found

    # Return the extracted artist and title, or just title if artist is not provided
    return title.strip(), (artist.strip() if artist else None)

def extract_rasa_entities(entities: List[Dict[str, str]]) -> SongDetails:
    song_details = SongDetails()
    for entity in entities:
        entity_type = entity['entity']
        value = entity['value']
        if entity_type == IntentType.SONG.value:
            song_details.title = value
        elif entity_type == IntentType.ARTIST.value:
            song_details.artist = value
        elif entity_type == IntentType.ALBUM.value:
            song_details.album = value
    return song_details