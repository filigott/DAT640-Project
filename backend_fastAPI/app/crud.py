from sqlalchemy import or_
from sqlalchemy.orm import Session
from .models import Playlist as PlaylistModel, Song as SongModel


def get_playlist(db: Session, playlist_id: int) -> PlaylistModel:
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

    return song

async def remove_song_from_playlist(db: Session, playlist_id: int, song_id: int):
    playlist = get_playlist(db, playlist_id)
    song = db.query(SongModel).filter(SongModel.id == song_id).first()
    if playlist and song and song in playlist.songs:
        playlist.songs.remove(song)
        db.commit()

async def db_clear_playlist(db: Session, playlist_id: int):
    playlist = get_playlist(db, playlist_id)
    if playlist:
        playlist.songs = []
        db.commit()


# Does not work
def bot_get_song_id(db: Session, song_description: dict) -> int:
    # Build the query conditions based on the provided description
    filters = []
    if 'title' in song_description:
        filters.append(SongModel.title.ilike(f"%{song_description['title']}%"))
    if 'artist' in song_description:
        filters.append(SongModel.artist.ilike(f"%{song_description['artist']}%"))
    if 'album' in song_description:
        filters.append(SongModel.album.ilike(f"%{song_description['album']}%"))
    if 'year' in song_description:
        filters.append(SongModel.year == song_description['year'])

    # Use OR to match any of the provided fields, or AND if all fields must match.
    try:
        song = db.query(SongModel).filter(or_(*filters)).first()
        return song.id if song else None
    except Exception as e:
        return None
    

def bot_get_song_id_by_name(db: Session, song_description: str) -> int:
    song_name = song_description["data"].get("title")
    print("song name: ", song_name)
    song = db.query(SongModel).filter(SongModel.title == song_name).first()
    return song.id if song else None