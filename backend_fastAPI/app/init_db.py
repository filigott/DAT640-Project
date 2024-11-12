import sqlite3
from sqlalchemy.orm import Session

from app.utils import advanced_normalize_text
from .models import PlaylistModel, SongModel, PlaylistSongsTable
from sqlalchemy.orm import Session


def reset_db(db: Session):
    try:
        # Check if the PlaylistSongsTable exists before trying to delete from it
        if db.execute("SELECT to_regclass('public.playlist_songs')").fetchone()[0]:
            db.execute(PlaylistSongsTable.delete())
            print("Deleted records from playlist_songs table.")
        
        # Delete records from SongModel and PlaylistModel if the tables exist
        if db.execute("SELECT to_regclass('public.songs')").fetchone()[0]:
            db.query(SongModel).delete()
            print("Deleted records from songs table.")
        
        if db.execute("SELECT to_regclass('public.playlists')").fetchone()[0]:
            db.query(PlaylistModel).delete()
            print("Deleted records from playlists table.")

        db.commit()

        # Reset the primary key sequence if the tables exist
        if db.execute("SELECT to_regclass('public.songs_id_seq')").fetchone()[0]:
            db.execute('ALTER SEQUENCE songs_id_seq RESTART WITH 1')
            print("Reset songs_id_seq.")
        
        if db.execute("SELECT to_regclass('public.playlists_id_seq')").fetchone()[0]:
            db.execute('ALTER SEQUENCE playlists_id_seq RESTART WITH 1')
            print("Reset playlists_id_seq.")

        db.commit()
        
        print("Database reset successfully.")
        
    except Exception as e:
        db.rollback()
        print(f"Error resetting the database: {e}")


def get_or_create_song(db: Session, title: str, artist: str, album: str, year: int) -> SongModel:
    """Helper function to fetch or create a song in the database."""
    normalized_title = advanced_normalize_text(title)
    
    song = db.query(SongModel).filter(
        SongModel.title == title,
        SongModel.artist == artist,
        SongModel.year == year
    ).first()
    
    if not song:
        song = SongModel(title=title, artist=artist, album=album, year=year, normalized_title=normalized_title)
        db.add(song)
        db.commit()
        db.refresh(song)
    
    return song

def add_demo_songs_to_playlist(db: Session, playlist_id: int):
    """Helper function to add predefined demo songs to a playlist."""
    song_titles = [
        "Shape of You", "Blinding Lights", "Levitating", 
        "Bad Guy", "Watermelon Sugar"
    ]
    artist_map = {
        "Shape of You": "Ed Sheeran",
        "Blinding Lights": "The Weeknd",
        "Levitating": "Dua Lipa",
        "Bad Guy": "Billie Eilish",
        "Watermelon Sugar": "Harry Styles"
    }
    album_map = {
        "Shape of You": "Divide",
        "Blinding Lights": "After Hours",
        "Levitating": "Future Nostalgia",
        "Bad Guy": "When We All Fall Asleep",
        "Watermelon Sugar": "Fine Line"
    }
    year_map = {
        "Shape of You": 2017,
        "Blinding Lights": 2020,
        "Levitating": 2020,
        "Bad Guy": 2019,
        "Watermelon Sugar": 2019
    }

    songs_to_add = []
    for title in song_titles:
        artist = artist_map.get(title)
        album = album_map.get(title)
        year = year_map.get(title)

        song = get_or_create_song(db, title, artist, album, year)
        songs_to_add.append(song)

    playlist: PlaylistModel = db.query(PlaylistModel).filter(PlaylistModel.id == playlist_id).first()

    if not playlist:
        playlist = PlaylistModel(title="My Favorite Songs", songs=songs_to_add)
        db.add(playlist)
    else:
        playlist.songs.extend(songs_to_add)

    db.commit()
    print(f"Added demo songs to playlist {playlist_id}.")


def seed_db_demo(db: Session):
    """Seeds the database with manually defined demo songs and adds them to a playlist."""
    try:
        add_demo_songs_to_playlist(db, playlist_id=1)
        print("Database seeded successfully with demo songs.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")


def seed_db_dataset_sqlite(db: Session, sqlite_db_path: str):
    """Seeds the database with songs from an SQLite dataset and adds demo songs to a playlist."""
    reset_db(db)

    try:
        # Connect to the SQLite database
        sqlite_conn = sqlite3.connect(sqlite_db_path)
        cursor = sqlite_conn.cursor()

        # Query the acoustic_features table
        cursor.execute("""
            SELECT song, artist, album, date, duration_ms, tempo, acousticness, danceability, energy, 
                instrumentalness, key, liveness, loudness, mode, speechiness, valence
            FROM acoustic_features
        """)
        rows = cursor.fetchall()

        print("first row: ", rows[0])

        # Transform and insert into PostgreSQL
        songs = []
        for row in rows:
            title = row[0] if row[0] is not None else 'Unknown Title'  # Handle missing titles
            artist = row[1] if row[1] is not None else 'Unknown Artist'  # Handle missing artists
            album = row[2] if row[2] is not None else 'Unknown Album'  # Handle missing albums
            year = int(row[3].split('-')[0]) if row[3] else None  # Extract year from release date
            duration = (row[4] // 1000) if row[4] is not None else None  # Handle missing duration
            tempo = row[5] if row[5] is not None else None  # Handle missing tempo
            normalized_title = advanced_normalize_text(title)

            # New acoustic features
            acousticness = row[6] if row[6] is not None else None
            danceability = row[7] if row[7] is not None else None
            energy = row[8] if row[8] is not None else None
            instrumentalness = row[9] if row[9] is not None else None
            key = row[10] if row[10] is not None else None
            liveness = row[11] if row[11] is not None else None
            loudness = row[12] if row[12] is not None else None
            mode = row[13] if row[13] is not None else None
            speechiness = row[14] if row[14] is not None else None
            valence = row[15] if row[15] is not None else None

            song = SongModel(
                title=title,
                artist=artist,
                album=album,
                year=year,
                duration=duration,
                tempo=tempo,
                normalized_title=normalized_title,

                acousticness=acousticness,
                danceability=danceability,
                energy=energy,
                instrumentalness=instrumentalness,
                key=key,
                liveness=liveness,
                loudness=loudness,
                mode=mode,
                speechiness=speechiness,
                valence=valence,
            )
            songs.append(song)

        # Insert all songs into the PostgreSQL database
        batch_size = 10000
        for i in range(0, len(songs), batch_size):
            batch_songs = songs[i:i+batch_size]
            db.bulk_save_objects(batch_songs)

            batch_number = (i // batch_size) + 1
            print(f"Batch: {batch_number}, inserted {len(batch_songs)} songs from SQLite to PostgreSQL.")
            db.commit()

        print(f"Inserted {len(songs)} total songs from SQLite to PostgreSQL.")

        # Add the demo songs to the playlist with id = 1
        add_demo_songs_to_playlist(db, playlist_id=1)

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")

    finally:
        # Close SQLite connection
        if cursor:
            cursor.close()
        if sqlite_conn:
            sqlite_conn.close()