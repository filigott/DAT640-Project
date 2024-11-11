import random
from typing import Optional, List
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from rapidfuzz import process

from app.init_db import seed_db_demo
from app.utils import advanced_normalize_text
from ..models import PlaylistModel, SongModel

MAX_NUM_SONGS_SEARCH = 10
RAPIDFUZZ_SCORE_CUTOFF = 70

def demo_seed_database(db: Session):
    seed_db_demo(db)

def get_all_playlists(db: Session) -> List[PlaylistModel]:
    """Retrieve all playlists from the database as raw models."""
    return db.query(PlaylistModel).all()

def get_all_songs(db: Session) -> List[SongModel]:
    """Retrieve all songs from the database as raw models."""
    return db.query(SongModel).all()

def get_playlist(db: Session, playlist_id: int) -> Optional[PlaylistModel]:
    """Retrieve a specific playlist by ID and return the raw model."""
    return db.query(PlaylistModel).filter(PlaylistModel.id == playlist_id).first()

def get_search_songs_not_in_playlist(db: Session, playlist_id: int, search_field: str = "") -> List[SongModel]:
    """Retrieve a maximum of 10 songs not in a specific playlist matching a search field."""
    
    # Create a query to fetch songs not in the specified playlist
    query = db.query(SongModel).filter(~SongModel.playlists.any(id=playlist_id))

    # If there's a search term, filter the query based on the search field
    if search_field:
        search = f"%{search_field.lower()}%"
        query = query.filter(
            (SongModel.title.ilike(search)) | 
            (SongModel.artist.ilike(search))
        )

    # Limit the query to 10 results
    return query.limit(MAX_NUM_SONGS_SEARCH).all()

async def add_song_to_playlist_async(db: Session, playlist_id: int, song_id: int) -> Optional[SongModel]:
    """Add a song to a specific playlist and return the added song."""
    playlist = get_playlist(db, playlist_id)
    song = db.query(SongModel).filter(SongModel.id == song_id).first()
    
    if playlist and song and song not in playlist.songs:
        playlist.songs.append(song)
        db.commit()
        return song
    return None

def add_song_to_playlist(db: Session, playlist_id: int, song_id: int) -> Optional[SongModel]:
    """Add a song to a specific playlist and return the added song."""
    playlist = get_playlist(db, playlist_id)
    song = db.query(SongModel).filter(SongModel.id == song_id).first()
    
    if playlist and song and song not in playlist.songs:
        playlist.songs.append(song)
        db.commit()
        return song
    return None

async def remove_song_from_playlist_async(db: Session, playlist_id: int, song_id: int) -> Optional[SongModel]:
    """Remove a song from a specific playlist and return the removed song."""
    playlist = get_playlist(db, playlist_id)
    song = db.query(SongModel).filter(SongModel.id == song_id).first()

    if playlist and song and song in playlist.songs:
        playlist.songs.remove(song)
        db.commit()
        return song
    return None

def remove_song_from_playlist(db: Session, playlist_id: int, song_id: int) -> Optional[SongModel]:
    """Remove a song from a specific playlist and return the removed song."""
    playlist = get_playlist(db, playlist_id)
    song = db.query(SongModel).filter(SongModel.id == song_id).first()

    if playlist and song and song in playlist.songs:
        playlist.songs.remove(song)
        db.commit()
        return song
    return None

def clear_playlist(db: Session, playlist_id: int):
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

def get_song_by_song_description(db: Session, song_description: dict) -> Optional[int]:
    """Get a song ID based on the song title."""
     # If 'id' is already provided in the description, return it directly
    song_id = song_description.get("id")
    if song_id:
        return song_id
    
    song_name = song_description.get("title")
    artist_name = song_description.get("artist")
    ##album_name = song_description["data"].get("album")
    if not song_name:
        return None
    
    if song_name and artist_name:
        song = db.query(SongModel).filter(SongModel.title == song_name, SongModel.artist == artist_name).first()
        return song.id if song else None

    song: SongModel = db.query(SongModel).filter(SongModel.title == song_name).first()
    return song.id if song else None

def get_songs_by_name(db: Session, song_name: str) -> List[SongModel]:
    """Get a list of songs based on the song title."""
    if not song_name:
        return []
    songs = db.query(SongModel).filter(SongModel.title.ilike(f"%{song_name}%")).all()
    print(songs)
    return songs

def get_songs_by_artist(db: Session, artist_name: str) -> List[SongModel]:
    """Get a list of songs based on the artist name."""
    if not artist_name:
        return []
  
    songs = db.query(SongModel).filter(SongModel.artist.ilike(f"%{artist_name}%")).all()
    if songs:
        return songs
    else:
        all_artists = db.query(SongModel.artist).distinct().all()
        artist_names = [artist[0] for artist in all_artists] 

        best_match = process.extractOne(artist_name, artist_names, score_cutoff=RAPIDFUZZ_SCORE_CUTOFF)
        if best_match:
            songs = db.query(SongModel).filter(SongModel.artist == best_match[0]).all()
            return songs
        return songs

def get_songs_by_album(db: Session, album_name: str) -> List[SongModel]:
    """Get a list of songs based on the album name."""
    if not album_name:
        return []
    songs = db.query(SongModel).filter(SongModel.album.ilike(f"%{album_name}%")).all()
    return songs

def get_recommendations_from_playlist(db: Session, playlist_id: int = 1, num_recommendations: int = 10) -> List[SongModel]:
    playlist = get_playlist(db, playlist_id)

    # artists = set(song['artist'] for song in playlist.songs)
    # albums = set(song['album'] for song in playlist.songs)
    # titles = set(song['title'] for song in playlist.songs)

    artists = set(song.artist for song in playlist.songs)
    albums = set(song.album for song in playlist.songs)
    titles = set(song.title for song in playlist.songs)

    songs = db.query(SongModel).filter((
        SongModel.artist.in_(artists)), 
        SongModel.title.notin_(titles)
    ).all()

    random_recommendations = random.sample(songs, num_recommendations)

    return random_recommendations


def find_fuzzy_song_matches(
    db: Session, 
    title: str, 
    artist: Optional[str] = None, 
    album: Optional[str] = None, 
    year: Optional[int] = None
) -> List[SongModel]:
    """Find songs that match the specified criteria with flexible matching."""

    # Normalize the input title for fuzzy matching
    normalized_title = advanced_normalize_text(title)

    # Start the query with ilike to allow partial matches on the normalized title
    query = db.query(SongModel).filter(SongModel.normalized_title.ilike(f"%{normalized_title}%"))
    
    if artist:
        query = query.filter(SongModel.artist.ilike(f"%{artist}%"))
    if album:
        query = query.filter(SongModel.album.ilike(f"%{album}%"))
    if year:
        query = query.filter(SongModel.year == year)
    
    # Retrieve initial candidates using the ilike query
    candidates: List[SongModel] = query.limit(50).all()

    print("Num fuzzy song matches candidates: ", len(candidates))
    
    # Normalize the titles of all candidates for better matching
    candidate_titles = [advanced_normalize_text(c.title) for c in candidates]
    
    # Perform fuzzy matching using the normalized title
    scored_candidates = process.extract(normalized_title, candidate_titles, score_cutoff=RAPIDFUZZ_SCORE_CUTOFF)
    
    # Map back to SongModel objects using the index of matches in scored_candidates
    matched_songs = [candidates[idx] for _, score, idx in scored_candidates]
    
    return matched_songs[:MAX_NUM_SONGS_SEARCH]


def find_exact_song_match(
    db: Session, 
    title: str, 
    artist: Optional[str] = None, 
    album: Optional[str] = None, 
    year: Optional[int] = None
) -> Optional[SongModel]:
    """Attempts to find a song with an exact match on title, artist, album, and year."""

    # Apply exact filters for title, artist, album, and year
    filters = [SongModel.title == title]
    if artist:
        filters.append(SongModel.artist == artist)
    if album:
        filters.append(SongModel.album == album)
    if year:
        filters.append(SongModel.year == year)

    # Query with all filters applied. NB! need limit higher than 1
    matched_songs = db.query(SongModel).filter(and_(*filters)).limit(2).all()
    
    return matched_songs[0] if len(matched_songs) == 1 else None