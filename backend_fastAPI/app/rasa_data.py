import random
import re
from requests import Session

from app.models import SongModel


def preprocess_name(name):
    # Remove unnecessary punctuation, keeping alphanumeric characters, spaces, apostrophes, hyphens, and parentheses
    name = re.sub(r"[^\w\s'\-()]", "", name)
    return name.strip()

def clean_and_filter_data(data_list):
    # Filter out empty strings and invalid entries (e.g., too short or non-useful data)
    valid_entries = []
    for entry in data_list:
        entry = preprocess_name(entry)  # Apply preprocessing
        if entry and len(entry) > 2 and not entry.isdigit():  # Skip empty or numeric-only entries
            valid_entries.append(entry)
    return valid_entries

def sample_data(data_list, sample_percentage=0.1, seed=42):
    # Set the seed for deterministic sampling
    random.seed(seed)
    
    # Randomly sample some % of the data (rounded to the nearest integer)
    sample_size = int(len(data_list) * sample_percentage)
    return random.sample(data_list, sample_size)

def random_case_variation(text, variation_probability=0.1):
    if random.random() < variation_probability:
        return random.choice([text.lower(), text.upper(), text.title()])
    return text  # Return original text if variation is not applied


def save_data_to_disk(db: Session):
    all_songs = db.query(SongModel.title).distinct().all()
    all_songs_normalized = db.query(SongModel.normalized_title).distinct().all()
    all_artists = db.query(SongModel.artist).distinct().all()
    all_albums = db.query(SongModel.album).distinct().all()

    # Clean and filter original song titles and normalized song titles
    print("Num total songs: ", len(all_songs))
    valid_songs = clean_and_filter_data([song.title for song in all_songs])
    valid_songs_normalized = clean_and_filter_data([song[0] for song in all_songs_normalized])
    print("Num valid songs (original): ", len(valid_songs))
    print("Num valid songs (normalized): ", len(valid_songs_normalized))

    # Sample 10% from both valid songs and valid normalized songs
    sampled_songs = sample_data(valid_songs, 0.1)
    sampled_normalized_songs = sample_data(valid_songs_normalized, 0.1)
    print("Num sampled songs (original): ", len(sampled_songs))
    print("Num sampled songs (normalized): ", len(sampled_normalized_songs))

    # Combine sampled original and normalized titles
    final_song_list = sampled_songs + sampled_normalized_songs

    # Save cleaned, sampled, and varied song titles to disk
    with open("all_songs.yml", "w", encoding="utf-8") as f:
        f.write('version: "3.1"\n')
        f.write('nlu:\n')
        f.write('- lookup: song\n')
        f.write('  examples: |\n')
        
        for song in final_song_list:
            f.write(f"    - {random_case_variation(song)}\n")

    # Clean and filter artist names
    print("Num total artists: ", len(all_artists))
    valid_artists = clean_and_filter_data([artist[0] for artist in all_artists])
    print("Num valid artists: ", len(valid_artists))

    # Save cleaned and filtered artist names with occasional case variations
    with open("all_artists.yml", "w", encoding="utf-8") as f:
        f.write('version: "3.1"\n')
        f.write('nlu:\n')
        f.write('- lookup: artist\n')
        f.write('  examples: |\n')

        for artist in valid_artists:
            f.write(f"    - {random_case_variation(artist)}\n")

    # Clean and filter album titles
    print("Num total albums: ", len(all_albums))
    valid_albums = clean_and_filter_data([album[0] for album in all_albums])
    print("Num valid albums: ", len(valid_albums))

    # Save cleaned and filtered album titles with occasional case variations
    with open("all_albums.yml", "w", encoding="utf-8") as f:
        f.write('version: "3.1"\n')
        f.write('nlu:\n')
        f.write('- lookup: album\n')
        f.write('  examples: |\n')

        for album in valid_albums:
            f.write(f"    - {random_case_variation(album)}\n")