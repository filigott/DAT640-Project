import sqlite3
from sqlalchemy.orm import Session
from .models import PlaylistModel, SongModel, PlaylistSongsTable
from sqlalchemy.orm import Session


def reset_db(db: Session):
    try:
        # Delete all records from the playlist_songs join table first
        db.execute(PlaylistSongsTable.delete())

        # Now delete all records from SongModel and PlaylistModel
        db.query(SongModel).delete()
        db.query(PlaylistModel).delete()
        db.commit()

        # Reset the primary key sequence to start from 1 (optional)
        db.execute('ALTER SEQUENCE songs_id_seq RESTART WITH 1')
        db.execute('ALTER SEQUENCE playlists_id_seq RESTART WITH 1')
        db.commit()

        print("Database reset successfully.")
        
    except Exception as e:
        db.rollback()
        print(f"Error resetting the database: {e}")


def seed_db_demo(db: Session):
    reset_db(db)

    try:
        # Create demo songs with artist, album, and year information
        songs = [
            SongModel(title="Shape of You", artist="Ed Sheeran", album="Divide", year=2017),
            SongModel(title="Blinding Lights", artist="The Weeknd", album="After Hours", year=2020),
            SongModel(title="Levitating", artist="Dua Lipa", album="Future Nostalgia", year=2020),
            SongModel(title="Bad Guy", artist="Billie Eilish", album="When We All Fall Asleep", year=2019),
            SongModel(title="Watermelon Sugar", artist="Harry Styles", album="Fine Line", year=2019),
        ]
        db.add_all(songs)
        db.commit()

        # Create a playlist and add the songs
        playlist = PlaylistModel(title="My Favorite Songs", songs=songs)
        db.add(playlist)
        db.commit()

        print("Database seeded successfully.")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")



def seed_db_dataset_sqlite(db: Session, sqlite_db_path: str):
    # TODO: Get large dataset and seed data into respective tables
    reset_db(db)

    try:
        # Connect to the SQLite database
        sqlite_conn = sqlite3.connect(sqlite_db_path)
        cursor = sqlite_conn.cursor()

        # Query the acoustic_features table
        cursor.execute("SELECT song, artist, album, date, duration_ms FROM acoustic_features")
        rows = cursor.fetchall()

        print("first row: ", rows[0])

        # Transform and insert into PostgreSQL
        songs = []
        for row in rows:
            title = row[0] if row[0] is not None else 'Unknown Title'  # Handle missing titles
            artist = row[1] if row[1] is not None else 'Unknown Artist'  # Handle missing artists
            album = row[2] if row[2] is not None else 'Unknown Album'  # Handle missing albums
            year = int(row[3].split('-')[0]) if row[3] else 0  # Extract year from release date
            duration = (row[4] // 1000) if row[4] is not None else 0  # Handle missing duration

            song = SongModel(
                title=title,
                artist=artist,
                album=album,
                year=year,
                duration=duration
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

        # Create a playlist
        playlist = PlaylistModel(title="My Favorite Songs", songs=[])
        db.add(playlist)
        db.commit()

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")

    finally:
        # Close SQLite connection
        if cursor:
            cursor.close()
        if sqlite_conn:
            sqlite_conn.close()