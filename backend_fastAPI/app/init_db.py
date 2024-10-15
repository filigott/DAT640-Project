from sqlalchemy.orm import Session
from .models import PlaylistModel, SongModel

from sqlalchemy.orm import Session

def reset_and_seed_db_demo(db: Session):
    # Delete all existing data to start fresh
    db.query(SongModel).delete()
    db.query(PlaylistModel).delete()
    db.commit()

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




def seed_db_dataset(db: Session):
    # TODO: Get large dataset and seed data into respective tables
    ...