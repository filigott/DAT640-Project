from sqlalchemy.orm import Session
from .models import Song, Playlist

def seed_db(db: Session):
    # Check if data already exists to avoid duplicates
    if db.query(Song).count() == 0 and db.query(Playlist).count() == 0:
        # Create demo songs
        songs = [
            Song(title="Shape of You", artist="Ed Sheeran", album="Divide", year=2017),
            Song(title="Blinding Lights", artist="The Weeknd", album="After Hours", year=2020),
            Song(title="Levitating", artist="Dua Lipa", album="Future Nostalgia", year=2020),
            Song(title="Bad Guy", artist="Billie Eilish", album="When We All Fall Asleep", year=2019),
            Song(title="Watermelon Sugar", artist="Harry Styles", album="Fine Line", year=2019),
        ]

        # Add songs to DB
        db.add_all(songs)
        db.commit()

        # Create a playlist and add the songs
        playlist = Playlist(name="My Favorite Songs", description="A collection of great tracks")
        playlist.songs.extend(songs)

        # Add the playlist to DB
        db.add(playlist)
        db.commit()