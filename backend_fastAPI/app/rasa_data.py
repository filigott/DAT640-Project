import json
import os
from typing import List
from requests import Session
from app.models import SongModel
from app.utils import clean_and_filter_data, random_case_variation

# Get the absolute path of the current script (rasa_data.py)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the data folder
RASA_DATA_FOLDER_PATH = os.path.join(script_dir, "../../rasa_agent/data")

# Ensure the RASA_DATA_FOLDER_PATH exists, if not, create it
os.makedirs(RASA_DATA_FOLDER_PATH, exist_ok=True)

def save_data_to_disk(db: Session):
    # Query unique song, artist, and album entries from the database
    all_songs: List[SongModel] = db.query(SongModel.title, SongModel.normalized_title).distinct().all()
    all_artists = db.query(SongModel.artist).distinct().all()
    all_albums = db.query(SongModel.album).distinct().all()

    # Clean and filter data
    valid_songs = set(clean_and_filter_data([song.title for song in all_songs]))
    valid_song_normalized = {song.normalized_title: song.title for song in all_songs}
    valid_artists = clean_and_filter_data([artist[0] for artist in all_artists])
    valid_albums = clean_and_filter_data([album[0] for album in all_albums])

    # Accumulate all songs data (only songs that exist in valid_songs set)
    all_songs_data = []
    for norm_song, song in valid_song_normalized.items():
        if song in valid_songs:
            all_songs_data.append(song)
            all_songs_data.append(norm_song)

    # Accumulate artist and album data with random case variations
    all_artists_data = [random_case_variation(artist) for artist in valid_artists]
    all_albums_data = [random_case_variation(album) for album in valid_albums]

    # Save the data to Rasa-compatible YAML files
    def write_yaml_file(filename, lookup_name, items):
        with open(f"{RASA_DATA_FOLDER_PATH}/{filename}", "w", encoding="utf-8") as f:
            f.write("version: '3.1'\n")
            f.write(f"nlu:\n- lookup: {lookup_name}\n  examples: |\n")
            for item in items:
                f.write(f"    - {item}\n")

    # Write songs, artists, and albums data to separate YAML files
    write_yaml_file("all_songs.yml", "song", all_songs_data)
    write_yaml_file("all_artists.yml", "artist", all_artists_data)
    write_yaml_file("all_albums.yml", "album", all_albums_data)
