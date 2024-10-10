from sqlalchemy.orm import Session
from .models import Playlist as PlaylistModel, Song as SongModel


def get_playlist(db: Session, playlist_id: int):
    return db.query(PlaylistModel).filter(PlaylistModel.id == playlist_id).first()


def get_all_playlists(db: Session):
    return db.query(PlaylistModel).all()


def get_all_songs(db: Session):
    return db.query(SongModel).all()


def get_songs_not_in_playlist(db: Session, playlist_id: int):
    playlist = get_playlist(db, playlist_id)
    if not playlist:
        return []
    all_songs = db.query(SongModel).all()
    return [song for song in all_songs if song not in playlist.songs]


async def add_song_to_playlist(db: Session, playlist_id: int, song_id: int):
    playlist = get_playlist(db, playlist_id)
    song = db.query(SongModel).filter(SongModel.id == song_id).first()
    if playlist and song and song not in playlist.songs:
        playlist.songs.append(song)
        db.commit()


async def remove_song_from_playlist(db: Session, playlist_id: int, song_id: int):
    playlist = get_playlist(db, playlist_id)
    song = db.query(SongModel).filter(SongModel.id == song_id).first()
    if playlist and song and song in playlist.songs:
        playlist.songs.remove(song)
        db.commit()
