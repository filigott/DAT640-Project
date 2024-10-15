from typing import Optional, List
from sqlalchemy import or_
from sqlalchemy.orm import Session
from .models import PlaylistModel, SongModel
from .schemas import PlaylistSchema, SongSchema


def get_all_playlists(db: Session) -> List[PlaylistModel]:
    """Retrieve all playlists from the database as raw models."""
    return db.query(PlaylistModel).all()

def get_all_songs(db: Session) -> List[SongModel]:
    """Retrieve all songs from the database as raw models."""
    return db.query(SongModel).all()

def get_playlist(db: Session, playlist_id: int) -> Optional[PlaylistModel]:
    """Retrieve a specific playlist by ID and return the raw model."""
    return db.query(PlaylistModel).filter(PlaylistModel.id == playlist_id).first()

def get_songs_not_in_playlist(db: Session, playlist_id: int) -> List[SongModel]:
    """Retrieve songs not in a specific playlist."""
    playlist = get_playlist(db, playlist_id)
    if not playlist:
        return []
    
    all_songs = db.query(SongModel).all()
    return [song for song in all_songs if song not in playlist.songs]

async def add_song_to_playlist(db: Session, playlist_id: int, song_id: int) -> Optional[SongModel]:
    """Add a song to a specific playlist and return the added song."""
    playlist = get_playlist(db, playlist_id)
    song = db.query(SongModel).filter(SongModel.id == song_id).first()
    
    if playlist and song and song not in playlist.songs:
        playlist.songs.append(song)
        db.commit()
        return song
    return None

async def remove_song_from_playlist(db: Session, playlist_id: int, song_id: int) -> Optional[SongModel]:
    """Remove a song from a specific playlist and return the removed song."""
    playlist = get_playlist(db, playlist_id)
    song = db.query(SongModel).filter(SongModel.id == song_id).first()

    if playlist and song and song in playlist.songs:
        playlist.songs.remove(song)
        db.commit()
        return song
    return None

async def db_clear_playlist(db: Session, playlist_id: int):
    """Clear all songs from a specific playlist."""
    playlist = get_playlist(db, playlist_id)
    if playlist:
        playlist.songs = []
        db.commit()

def get_song_id(db: Session, song_description: dict) -> Optional[int]:
    """Get a song ID based on a description (title, artist, album, year)."""
    filters = []
    if 'title' in song_description:
        filters.append(SongModel.title.ilike(f"%{song_description['title']}%"))
    if 'artist' in song_description:
        filters.append(SongModel.artist.ilike(f"%{song_description['artist']}%"))
    if 'album' in song_description:
        filters.append(SongModel.album.ilike(f"%{song_description['album']}%"))
    if 'year' in song_description:
        filters.append(SongModel.year == song_description['year'])

    try:
        song: SongModel = db.query(SongModel).filter(or_(*filters)).first()
        return song.id if song else None
    except Exception as e:
        print(f"Error fetching song ID: {e}")
        return None

def get_song_id_by_name(db: Session, song_description: dict) -> Optional[int]:
    """Get a song ID based on the song title."""
    song_name = song_description.get("title")
    if not song_name:
        return None
    song: SongModel = db.query(SongModel).filter(SongModel.title == song_name).first()
    return song.id if song else None
